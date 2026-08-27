from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from focus.api.deps import current_user
from focus.extensions import db
from focus.models import FocusSession
from focus.models.focus_session import MODES
from focus.services.gamification import award_achievements, update_challenges

sessions_bp = Blueprint("sessions", __name__)

ACTIVE_STATUSES = ("running", "paused")


def active_session(user_id: int) -> FocusSession | None:
    return (
        FocusSession.query.filter(
            FocusSession.user_id == user_id, FocusSession.status.in_(ACTIVE_STATUSES)
        )
        .order_by(FocusSession.started_at.desc())
        .first()
    )


@sessions_bp.get("")
@jwt_required()
def list_sessions():
    user = current_user()
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    query = FocusSession.query.filter_by(user_id=user.id)
    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)
    pagination = query.order_by(FocusSession.started_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(
        {
            "sessions": [s.to_dict() for s in pagination.items],
            "page": pagination.page,
            "pages": pagination.pages,
            "total": pagination.total,
        }
    )


@sessions_bp.post("")
@jwt_required()
def start_session():
    user = current_user()
    if active_session(user.id):
        return jsonify({"error": "Ya tienes una sesión activa"}), 409

    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "pomodoro")
    if mode not in MODES:
        return jsonify({"error": f"Modo inválido, usa uno de {list(MODES)}"}), 400
    planned = int(data.get("planned_minutes") or 25)
    if not 1 <= planned <= 480:
        return jsonify({"error": "planned_minutes debe estar entre 1 y 480"}), 400

    session = FocusSession(
        user_id=user.id,
        mode=mode,
        planned_minutes=planned,
        tag=(data.get("tag") or None),
        source=data.get("source", "web"),
    )
    db.session.add(session)
    db.session.commit()
    return jsonify(session.to_dict()), 201


@sessions_bp.get("/active")
@jwt_required()
def get_active_session():
    session = active_session(current_user().id)
    return jsonify({"session": session.to_dict() if session else None})


@sessions_bp.post("/<int:session_id>/pause")
@jwt_required()
def pause_session(session_id: int):
    return _transition(session_id, pause=True)


@sessions_bp.post("/<int:session_id>/resume")
@jwt_required()
def resume_session(session_id: int):
    return _transition(session_id, pause=False)


def _transition(session_id: int, *, pause: bool):
    user = current_user()
    session = FocusSession.query.filter_by(id=session_id, user_id=user.id).first_or_404()
    try:
        if pause:
            session.pause()
        else:
            session.resume()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    db.session.commit()
    return jsonify(session.to_dict())


@sessions_bp.post("/<int:session_id>/complete")
@jwt_required()
def complete_session(session_id: int):
    user = current_user()
    session = FocusSession.query.filter_by(id=session_id, user_id=user.id).first_or_404()
    try:
        session.finish("completed")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409

    user.total_focus_points += session.points_earned
    unlocked = award_achievements(user, session)
    challenges = update_challenges(user, session)
    db.session.commit()
    return jsonify(
        {
            "session": session.to_dict(),
            "user": user.to_dict(),
            "unlocked_achievements": [ea.to_dict() for ea in unlocked],
            "challenge_updates": [p.to_dict() for p in challenges],
        }
    )


@sessions_bp.post("/<int:session_id>/abandon")
@jwt_required()
def abandon_session(session_id: int):
    user = current_user()
    session = FocusSession.query.filter_by(id=session_id, user_id=user.id).first_or_404()
    try:
        session.finish("abandoned")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    db.session.commit()
    return jsonify(session.to_dict())


@sessions_bp.delete("/<int:session_id>")
@jwt_required()
def delete_session(session_id: int):
    user = current_user()
    session = FocusSession.query.filter_by(id=session_id, user_id=user.id).first_or_404()
    if session.status == "completed":
        user.total_focus_points = max(0, user.total_focus_points - session.points_earned)
    db.session.delete(session)
    db.session.commit()
    return jsonify({"message": "Sesión eliminada"})
