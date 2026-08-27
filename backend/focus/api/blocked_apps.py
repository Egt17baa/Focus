from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from focus.api.deps import current_user
from focus.api.sessions import active_session
from focus.extensions import db
from focus.models import BlockedApp

blocked_apps_bp = Blueprint("blocked_apps", __name__)


def _in_schedule(schedule: list[dict], moment: datetime) -> bool:
    for slot in schedule:
        days = slot.get("days") or list(range(7))
        if moment.weekday() not in days:
            continue
        start = slot.get("start", "00:00")
        end = slot.get("end", "23:59")
        if start <= moment.strftime("%H:%M") <= end:
            return True
    return False


@blocked_apps_bp.get("")
@jwt_required()
def list_apps():
    user = current_user()
    apps = BlockedApp.query.filter_by(user_id=user.id).order_by(BlockedApp.app_name).all()
    return jsonify({"apps": [app.to_dict() for app in apps]})


@blocked_apps_bp.post("")
@jwt_required()
def create_app():
    user = current_user()
    data = request.get_json(silent=True) or {}
    name = (data.get("app_name") or "").strip()
    if not name:
        return jsonify({"error": "app_name es obligatorio"}), 400
    package_name = (data.get("package_name") or "").strip() or None
    duplicate = BlockedApp.query.filter_by(user_id=user.id, app_name=name).first()
    if duplicate:
        return jsonify({"error": "Esa app ya está en tu lista"}), 409

    app = BlockedApp(
        user_id=user.id,
        app_name=name,
        package_name=package_name,
        category=data.get("category", "otras"),
        block_during_sessions=bool(data.get("block_during_sessions", True)),
    )
    app.schedule = data.get("schedule")
    db.session.add(app)
    db.session.commit()
    return jsonify(app.to_dict()), 201


@blocked_apps_bp.patch("/<int:app_id>")
@jwt_required()
def update_app(app_id: int):
    user = current_user()
    app = BlockedApp.query.filter_by(id=app_id, user_id=user.id).first_or_404()
    data = request.get_json(silent=True) or {}
    for field in ("app_name", "package_name", "category"):
        if data.get(field):
            setattr(app, field, str(data[field])[:200])
    for flag in ("is_active", "block_during_sessions"):
        if flag in data:
            setattr(app, flag, bool(data[flag]))
    if "schedule" in data:
        app.schedule = data["schedule"]
    db.session.commit()
    return jsonify(app.to_dict())


@blocked_apps_bp.delete("/<int:app_id>")
@jwt_required()
def delete_app(app_id: int):
    user = current_user()
    app = BlockedApp.query.filter_by(id=app_id, user_id=user.id).first_or_404()
    db.session.delete(app)
    db.session.commit()
    return jsonify({"message": "App eliminada"})


@blocked_apps_bp.post("/check")
@jwt_required()
def check_app():
    """Consulta usada por el cliente Android para decidir si debe bloquear una app."""
    user = current_user()
    data = request.get_json(silent=True) or {}
    package_name = (data.get("package_name") or "").strip()
    if not package_name:
        return jsonify({"error": "package_name es obligatorio"}), 400

    app = BlockedApp.query.filter_by(
        user_id=user.id, package_name=package_name, is_active=True
    ).first()
    if not app:
        return jsonify({"blocked": False, "reason": None})

    if app.block_during_sessions and active_session(user.id):
        return jsonify({"blocked": True, "reason": "focus_session"})
    if app.schedule and _in_schedule(app.schedule, datetime.now()):
        return jsonify({"blocked": True, "reason": "schedule"})
    return jsonify({"blocked": False, "reason": None})
