from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from focus.extensions import db

LEVELS = [
    (0, "Novato"),
    (1000, "Enfocado"),
    (5000, "Maestro del Enfoque"),
    (15000, "Zen Digital"),
    (40000, "Leyenda del Foco"),
]


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    total_focus_points = db.Column(db.Integer, default=0, nullable=False)
    daily_goal_minutes = db.Column(db.Integer, default=120, nullable=False)
    timezone_name = db.Column(db.String(64), default="UTC", nullable=False)
    theme = db.Column(db.String(16), default="system", nullable=False)
    avatar_emoji = db.Column(db.String(8), default="🎯", nullable=False)

    sessions = db.relationship(
        "FocusSession", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    blocked_apps = db.relationship(
        "BlockedApp", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    participations = db.relationship(
        "ChallengeParticipation", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    earned_achievements = db.relationship(
        "EarnedAchievement", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return bool(self.password_hash) and check_password_hash(self.password_hash, password)

    @property
    def level(self) -> int:
        return sum(1 for threshold, _ in LEVELS if self.total_focus_points >= threshold)

    @property
    def level_name(self) -> str:
        return LEVELS[self.level - 1][1]

    @property
    def points_to_next_level(self) -> int | None:
        if self.level >= len(LEVELS):
            return None
        return LEVELS[self.level][0] - self.total_focus_points

    @property
    def level_progress(self) -> float:
        """Fracción (0-1) del nivel actual completada."""
        if self.level >= len(LEVELS):
            return 1.0
        floor_points = LEVELS[self.level - 1][0]
        ceiling_points = LEVELS[self.level][0]
        span = ceiling_points - floor_points
        return round((self.total_focus_points - floor_points) / span, 4)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "total_focus_points": self.total_focus_points,
            "level": self.level,
            "level_name": self.level_name,
            "level_progress": self.level_progress,
            "points_to_next_level": self.points_to_next_level,
            "daily_goal_minutes": self.daily_goal_minutes,
            "timezone_name": self.timezone_name,
            "theme": self.theme,
            "avatar_emoji": self.avatar_emoji,
        }

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class RevokedToken(db.Model):
    __tablename__ = "revoked_tokens"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(64), unique=True, nullable=False, index=True)
    revoked_at = db.Column(db.DateTime, default=utcnow, nullable=False)
