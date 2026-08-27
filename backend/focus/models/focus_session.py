from focus.extensions import db
from focus.models.user import utcnow

MODES = ("pomodoro", "deep_work", "custom", "break")
STATUSES = ("running", "paused", "completed", "abandoned")


class FocusSession(db.Model):
    __tablename__ = "focus_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    mode = db.Column(db.String(20), default="pomodoro", nullable=False)
    status = db.Column(db.String(20), default="running", nullable=False, index=True)
    source = db.Column(db.String(20), default="web", nullable=False)
    tag = db.Column(db.String(60), nullable=True)

    planned_minutes = db.Column(db.Integer, default=25, nullable=False)
    focus_minutes = db.Column(db.Integer, default=0, nullable=False)
    interruptions = db.Column(db.Integer, default=0, nullable=False)
    paused_seconds = db.Column(db.Integer, default=0, nullable=False)
    points_earned = db.Column(db.Integer, default=0, nullable=False)

    started_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    paused_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    @property
    def elapsed_seconds(self) -> int:
        end = self.ended_at or (self.paused_at if self.status == "paused" else utcnow())
        return max(0, int((end - self.started_at).total_seconds()) - self.paused_seconds)

    def pause(self) -> None:
        if self.status != "running":
            raise ValueError("La sesión no está en curso")
        self.status = "paused"
        self.paused_at = utcnow()
        self.interruptions += 1

    def resume(self) -> None:
        if self.status != "paused" or self.paused_at is None:
            raise ValueError("La sesión no está pausada")
        self.paused_seconds += int((utcnow() - self.paused_at).total_seconds())
        self.paused_at = None
        self.status = "running"

    def finish(self, status: str = "completed") -> None:
        if self.status in ("completed", "abandoned"):
            raise ValueError("La sesión ya finalizó")
        if self.status == "paused":
            self.resume()
        self.ended_at = utcnow()
        self.focus_minutes = self.elapsed_seconds // 60
        self.status = status
        self.points_earned = self.score() if status == "completed" else 0

    def score(self) -> int:
        """Puntos por foco real, con bonus por constancia y penalización por cortes."""
        points = self.focus_minutes
        if self.focus_minutes >= 90:
            points += 30
        elif self.focus_minutes >= 50:
            points += 15
        elif self.focus_minutes >= 25:
            points += 5
        if self.focus_minutes >= self.planned_minutes:
            points += 10
        points -= 2 * self.interruptions
        return max(0, points)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "mode": self.mode,
            "status": self.status,
            "source": self.source,
            "tag": self.tag,
            "planned_minutes": self.planned_minutes,
            "focus_minutes": self.focus_minutes,
            "interruptions": self.interruptions,
            "paused_seconds": self.paused_seconds,
            "points_earned": self.points_earned,
            "elapsed_seconds": self.elapsed_seconds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }

    def __repr__(self) -> str:
        return f"<FocusSession {self.id} user={self.user_id} {self.status}>"
