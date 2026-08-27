import json

from focus.extensions import db
from focus.models.user import utcnow


class BlockedApp(db.Model):
    __tablename__ = "blocked_apps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    app_name = db.Column(db.String(100), nullable=False)
    package_name = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(40), default="otras", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    block_during_sessions = db.Column(db.Boolean, default=True, nullable=False)
    schedule_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    @property
    def schedule(self) -> list[dict]:
        """Franjas [{"days": [0-6], "start": "HH:MM", "end": "HH:MM"}]."""
        if not self.schedule_json:
            return []
        try:
            value = json.loads(self.schedule_json)
        except json.JSONDecodeError:
            return []
        return value if isinstance(value, list) else []

    @schedule.setter
    def schedule(self, value: list[dict] | None) -> None:
        self.schedule_json = json.dumps(value) if value else None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "app_name": self.app_name,
            "package_name": self.package_name,
            "category": self.category,
            "is_active": self.is_active,
            "block_during_sessions": self.block_during_sessions,
            "schedule": self.schedule,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
