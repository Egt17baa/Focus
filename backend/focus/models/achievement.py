from focus.extensions import db
from focus.models.user import utcnow

ACHIEVEMENT_TYPES = ("session_count", "total_minutes", "streak_days", "single_session")


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(60), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(8), default="🏅", nullable=False)
    achievement_type = db.Column(db.String(30), nullable=False)
    target_value = db.Column(db.Integer, nullable=False)
    points_reward = db.Column(db.Integer, default=0, nullable=False)

    earned = db.relationship(
        "EarnedAchievement", backref="achievement", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "achievement_type": self.achievement_type,
            "target_value": self.target_value,
            "points_reward": self.points_reward,
        }


class EarnedAchievement(db.Model):
    __tablename__ = "earned_achievements"
    __table_args__ = (db.UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey("achievements.id"), nullable=False)
    earned_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    points_awarded = db.Column(db.Integer, default=0, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "earned_at": self.earned_at.isoformat() if self.earned_at else None,
            "points_awarded": self.points_awarded,
            "achievement": self.achievement.to_dict() if self.achievement else None,
        }
