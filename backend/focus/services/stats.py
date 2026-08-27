from datetime import timedelta

from focus.extensions import db
from focus.models import FocusSession, User, utcnow
from focus.services.gamification import current_streak, longest_streak


def _sum_minutes(user_id: int, since=None) -> int:
    query = db.session.query(
        db.func.coalesce(db.func.sum(FocusSession.focus_minutes), 0)
    ).filter_by(user_id=user_id, status="completed")
    if since is not None:
        query = query.filter(FocusSession.started_at >= since)
    return int(query.scalar())


def daily_series(user_id: int, days: int = 30) -> list[dict]:
    start = (utcnow() - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = (
        db.session.query(
            db.func.date(FocusSession.started_at),
            db.func.sum(FocusSession.focus_minutes),
            db.func.count(FocusSession.id),
        )
        .filter(
            FocusSession.user_id == user_id,
            FocusSession.status == "completed",
            FocusSession.started_at >= start,
        )
        .group_by(db.func.date(FocusSession.started_at))
        .all()
    )
    by_day = {str(day): (int(minutes or 0), int(count)) for day, minutes, count in rows}
    series = []
    for offset in range(days):
        day = (start + timedelta(days=offset)).date().isoformat()
        minutes, count = by_day.get(day, (0, 0))
        series.append({"date": day, "minutes": minutes, "sessions": count})
    return series


def tag_breakdown(user_id: int, days: int = 30) -> list[dict]:
    start = utcnow() - timedelta(days=days)
    rows = (
        db.session.query(
            db.func.coalesce(FocusSession.tag, "sin etiqueta"),
            db.func.sum(FocusSession.focus_minutes),
        )
        .filter(
            FocusSession.user_id == user_id,
            FocusSession.status == "completed",
            FocusSession.started_at >= start,
        )
        .group_by(db.func.coalesce(FocusSession.tag, "sin etiqueta"))
        .order_by(db.func.sum(FocusSession.focus_minutes).desc())
        .all()
    )
    return [{"tag": tag, "minutes": int(minutes or 0)} for tag, minutes in rows]


def hourly_heatmap(user_id: int, days: int = 30) -> list[dict]:
    """Minutos de foco por hora del día: revela las franjas más productivas."""
    start = utcnow() - timedelta(days=days)
    rows = (
        db.session.query(FocusSession.started_at, FocusSession.focus_minutes)
        .filter(
            FocusSession.user_id == user_id,
            FocusSession.status == "completed",
            FocusSession.started_at >= start,
        )
        .all()
    )
    by_hour = dict.fromkeys(range(24), 0)
    for started_at, minutes in rows:
        by_hour[started_at.hour] += int(minutes or 0)
    return [{"hour": hour, "minutes": by_hour[hour]} for hour in range(24)]


def overview(user: User) -> dict:
    now = utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=6)
    completed = FocusSession.query.filter_by(user_id=user.id, status="completed")
    total_sessions = completed.count()
    total_minutes = _sum_minutes(user.id)
    today_minutes = _sum_minutes(user.id, today_start)
    abandoned = FocusSession.query.filter_by(user_id=user.id, status="abandoned").count()
    attempted = total_sessions + abandoned
    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "average_minutes": round(total_minutes / total_sessions, 1) if total_sessions else 0,
        "today_minutes": today_minutes,
        "week_minutes": _sum_minutes(user.id, week_start),
        "daily_goal_minutes": user.daily_goal_minutes,
        "daily_goal_progress": round(min(1.0, today_minutes / user.daily_goal_minutes), 4)
        if user.daily_goal_minutes
        else 0,
        "completion_rate": round(total_sessions / attempted, 4) if attempted else 0,
        "current_streak": current_streak(user.id),
        "longest_streak": longest_streak(user.id),
        "total_points": user.total_focus_points,
        "level": user.level,
        "level_name": user.level_name,
        "level_progress": user.level_progress,
    }
