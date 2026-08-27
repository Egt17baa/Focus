from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from focus.api.deps import current_user
from focus.extensions import db

users_bp = Blueprint("users", __name__)


@users_bp.get("/me")
@jwt_required()
def me():
    return jsonify(current_user().to_dict())


@users_bp.patch("/me")
@jwt_required()
def update_me():
    user = current_user()
    data = request.get_json(silent=True) or {}
    if "daily_goal_minutes" in data:
        goal = int(data["daily_goal_minutes"])
        if not 5 <= goal <= 1440:
            return jsonify({"error": "daily_goal_minutes debe estar entre 5 y 1440"}), 400
        user.daily_goal_minutes = goal
    for field in ("timezone_name", "theme", "avatar_emoji"):
        if field in data and data[field]:
            setattr(user, field, str(data[field])[:64])
    db.session.commit()
    return jsonify(user.to_dict())


@users_bp.delete("/me")
@jwt_required()
def delete_me():
    user = current_user()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Cuenta eliminada"})
