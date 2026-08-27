from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from focus.api.deps import current_user
from focus.extensions import db
from focus.models import Challenge, ChallengeParticipation, User, utcnow
from focus.models.challenge import CHALLENGE_METRICS

challenges_bp = Blueprint("challenges", __name__)


def _parse_date(value: str | None, default: datetime) -> datetime:
    if not value:
        return default
    return datetime.fromisoformat(value.replace("Z", "")).replace(tzinfo=None)


@challenges_bp.get("")
@jwt_required()
def list_challenges():
    user = current_user()
    only_open = request.args.get("open", "true").lower() != "false"
    query = Challenge.query
    if only_open:
        query = query.filter(Challenge.end_date >= utcnow())
    mine = {p.challenge_id: p for p in user.participations}
    challenges = query.order_by(Challenge.end_date.asc()).all()
    return jsonify(
        {"challenges": [c.to_dict(mine.get(c.id)) for c in challenges]}
    )


@challenges_bp.post("")
@jwt_required()
def create_challenge():
    user = current_user()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if len(title) < 3:
        return jsonify({"error": "El título debe tener al menos 3 caracteres"}), 400
    metric = data.get("metric", "minutes")
    if metric not in CHALLENGE_METRICS:
        return jsonify({"error": f"metric debe ser uno de {list(CHALLENGE_METRICS)}"}), 400
    target = int(data.get("target_value") or 0)
    if target <= 0:
        return jsonify({"error": "target_value debe ser positivo"}), 400

    now = utcnow()
    challenge = Challenge(
        title=title,
        description=data.get("description"),
        metric=metric,
        target_value=target,
        reward_points=int(data.get("reward_points") or 100),
        start_date=_parse_date(data.get("start_date"), now),
        end_date=_parse_date(data.get("end_date"), now + timedelta(days=7)),
        created_by=user.id,
    )
    if challenge.end_date <= challenge.start_date:
        return jsonify({"error": "end_date debe ser posterior a start_date"}), 400
    db.session.add(challenge)
    db.session.commit()
    return jsonify(challenge.to_dict()), 201


@challenges_bp.post("/<int:challenge_id>/join")
@jwt_required()
def join_challenge(challenge_id: int):
    user = current_user()
    challenge = db.get_or_404(Challenge, challenge_id)
    if not challenge.is_open:
        return jsonify({"error": "El reto no está abierto"}), 409
    if ChallengeParticipation.query.filter_by(user_id=user.id, challenge_id=challenge.id).first():
        return jsonify({"error": "Ya participas en este reto"}), 409
    participation = ChallengeParticipation(user_id=user.id, challenge_id=challenge.id)
    db.session.add(participation)
    db.session.commit()
    return jsonify(challenge.to_dict(participation)), 201


@challenges_bp.delete("/<int:challenge_id>/leave")
@jwt_required()
def leave_challenge(challenge_id: int):
    user = current_user()
    participation = ChallengeParticipation.query.filter_by(
        user_id=user.id, challenge_id=challenge_id
    ).first_or_404()
    db.session.delete(participation)
    db.session.commit()
    return jsonify({"message": "Has salido del reto"})


@challenges_bp.get("/<int:challenge_id>/leaderboard")
@jwt_required()
def challenge_leaderboard(challenge_id: int):
    db.get_or_404(Challenge, challenge_id)
    rows = (
        db.session.query(ChallengeParticipation, User)
        .join(User, User.id == ChallengeParticipation.user_id)
        .filter(ChallengeParticipation.challenge_id == challenge_id)
        .order_by(ChallengeParticipation.progress.desc())
        .limit(50)
        .all()
    )
    return jsonify(
        {
            "leaderboard": [
                {
                    "rank": index + 1,
                    "username": user.username,
                    "avatar_emoji": user.avatar_emoji,
                    "progress": participation.progress,
                    "completed": participation.completed,
                }
                for index, (participation, user) in enumerate(rows)
            ]
        }
    )
