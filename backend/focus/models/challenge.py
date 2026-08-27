from focus.extensions import db
from focus.models.user import utcnow

CHALLENGE_METRICS = ("minutes", "sessions")


class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    metric = db.Column(db.String(20), default="minutes", nullable=False)
    target_value = db.Column(db.Integer, nullable=False)
    reward_points = db.Column(db.Integer, default=0, nullable=False)
    start_date = db.Column(db.DateTime, default=utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    participations = db.relationship(
        "ChallengeParticipation", backref="challenge", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def is_open(self) -> bool:
        return self.start_date <= utcnow() <= self.end_date

    def to_dict(self, participation=None) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "metric": self.metric,
            "target_value": self.target_value,
            "reward_points": self.reward_points,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "participants": len(self.participations),
            "is_open": self.is_open,
        }
        if participation is not None:
            data["my_participation"] = participation.to_dict()
        return data


class ChallengeParticipation(db.Model):
    __tablename__ = "challenge_participations"
    __table_args__ = (db.UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False, index=True)
    progress = db.Column(db.Integer, default=0, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    points_earned = db.Column(db.Integer, default=0, nullable=False)
    joined_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "challenge_id": self.challenge_id,
            "progress": self.progress,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "points_earned": self.points_earned,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
        }
