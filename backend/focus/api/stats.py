from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from focus.api.deps import current_user
from focus.extensions import db
from focus.models import EarnedAchievement, User
from focus.services import stats as stats_service

stats_bp = Blueprint("stats", __name__)


@stats_bp.get("/overview")
@jwt_required()
def overview():
    user = current_user()
    days = min(request.args.get("days", 30, type=int), 365)
    return jsonify(
        {
            "overview": stats_service.overview(user),
            "daily": stats_service.daily_series(user.id, days),
            "tags": stats_service.tag_breakdown(user.id, days),
            "hours": stats_service.hourly_heatmap(user.id, days),
        }
    )


@stats_bp.get("/achievements")
@jwt_required()
def achievements():
    user = current_user()
    earned = (
        EarnedAchievement.query.filter_by(user_id=user.id)
        .order_by(EarnedAchievement.earned_at.desc())
        .all()
    )
    return jsonify({"earned": [ea.to_dict() for ea in earned]})


@stats_bp.get("/leaderboard")
@jwt_required()
def leaderboard():
    limit = min(request.args.get("limit", 20, type=int), 100)
    users = (
        db.session.query(User).order_by(User.total_focus_points.desc()).limit(limit).all()
    )
    me = current_user()
    return jsonify(
        {
            "leaderboard": [
                {
                    "rank": index + 1,
                    "username": user.username,
                    "avatar_emoji": user.avatar_emoji,
                    "points": user.total_focus_points,
                    "level_name": user.level_name,
                    "is_me": user.id == me.id,
                }
                for index, user in enumerate(users)
            ]
        }
    )
