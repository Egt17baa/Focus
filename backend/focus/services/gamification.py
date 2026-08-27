from datetime import date, timedelta

from focus.extensions import db
from focus.models import (
    Achievement,
    ChallengeParticipation,
    EarnedAchievement,
    FocusSession,
    User,
    utcnow,
)

SEED_ACHIEVEMENTS = [
    ("first_session", "Primer paso", "Completa tu primera sesión", "🚀", "session_count", 1, 50),
    ("ten_sessions", "Constancia", "Completa 10 sesiones", "🔁", "session_count", 10, 150),
    ("fifty_sessions", "Rutina sólida", "Completa 50 sesiones", "🏗️", "session_count", 50, 500),
    ("five_hours", "Cinco horas", "Acumula 300 minutos de foco", "⏳", "total_minutes", 300, 200),
    ("day_focus", "Día completo", "Acumula 1440 minutos de foco", "🌞", "total_minutes", 1440, 800),
    ("deep_dive", "Inmersión", "Una sesión de 90 minutos", "🤿", "single_session", 90, 300),
    ("streak_3", "Tres días", "Racha de 3 días con foco", "🔥", "streak_days", 3, 100),
    ("streak_7", "Semana perfecta", "Racha de 7 días con foco", "🗓️", "streak_days", 7, 300),
    ("streak_30", "Mes imparable", "Racha de 30 días con foco", "🏆", "streak_days", 30, 1500),
]


def seed_achievements() -> None:
    existing = {code for (code,) in db.session.query(Achievement.code).all()}
    for code, name, description, icon, kind, target, reward in SEED_ACHIEVEMENTS:
        if code in existing:
            continue
        db.session.add(
            Achievement(
                code=code,
                name=name,
                description=description,
                icon=icon,
                achievement_type=kind,
                target_value=target,
                points_reward=reward,
            )
        )
    db.session.commit()


def completed_sessions(user_id: int):
    return FocusSession.query.filter_by(user_id=user_id, status="completed")


def current_streak(user_id: int) -> int:
    days = {
        row[0].date()
        for row in db.session.query(FocusSession.started_at)
        .filter_by(user_id=user_id, status="completed")
        .all()
    }
    if not days:
        return 0
    today = utcnow().date()
    cursor = today if today in days else today - timedelta(days=1)
    if cursor not in days:
        return 0
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def longest_streak(user_id: int) -> int:
    days = sorted(
        {
            row[0].date()
            for row in db.session.query(FocusSession.started_at)
            .filter_by(user_id=user_id, status="completed")
            .all()
        }
    )
    best = run = 0
    previous: date | None = None
    for day in days:
        run = run + 1 if previous and day - previous == timedelta(days=1) else 1
        best = max(best, run)
        previous = day
    return best


def _progress_for(user_id: int, achievement: Achievement, session: FocusSession) -> int:
    if achievement.achievement_type == "session_count":
        return completed_sessions(user_id).count()
    if achievement.achievement_type == "total_minutes":
        return int(
            db.session.query(db.func.coalesce(db.func.sum(FocusSession.focus_minutes), 0))
            .filter_by(user_id=user_id, status="completed")
            .scalar()
        )
    if achievement.achievement_type == "single_session":
        return session.focus_minutes
    if achievement.achievement_type == "streak_days":
        return current_streak(user_id)
    return 0


def award_achievements(user: User, session: FocusSession) -> list[EarnedAchievement]:
    """Otorga los logros cuyo objetivo alcanzó el usuario tras cerrar una sesión."""
    already = {ea.achievement_id for ea in user.earned_achievements}
    newly: list[EarnedAchievement] = []
    for achievement in Achievement.query.all():
        if achievement.id in already:
            continue
        if _progress_for(user.id, achievement, session) >= achievement.target_value:
            earned = EarnedAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
                points_awarded=achievement.points_reward,
            )
            user.total_focus_points += achievement.points_reward
            db.session.add(earned)
            newly.append(earned)
    return newly


def update_challenges(user: User, session: FocusSession) -> list[ChallengeParticipation]:
    """Suma el progreso de la sesión a los retos abiertos del usuario."""
    updated: list[ChallengeParticipation] = []
    for participation in user.participations:
        challenge = participation.challenge
        if participation.completed or not challenge.is_open:
            continue
        participation.progress += (
            session.focus_minutes if challenge.metric == "minutes" else 1
        )
        if participation.progress >= challenge.target_value:
            participation.completed = True
            participation.completed_at = utcnow()
            participation.points_earned = challenge.reward_points
            user.total_focus_points += challenge.reward_points
        updated.append(participation)
    return updated
