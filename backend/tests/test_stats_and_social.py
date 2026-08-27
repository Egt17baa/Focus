from datetime import timedelta

from focus.extensions import db
from focus.models import FocusSession, utcnow


def seed_sessions(app, username: str = "eduardo") -> None:
    from focus.models import User

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        now = utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        for days_ago, minutes in ((0, 40), (1, 60), (2, 20)):
            started = (
                now - timedelta(minutes=1)
                if days_ago == 0
                else today_start - timedelta(days=days_ago) + timedelta(hours=12)
            )
            db.session.add(
                FocusSession(
                    user_id=user.id,
                    status="completed",
                    focus_minutes=minutes,
                    planned_minutes=minutes,
                    points_earned=minutes,
                    tag="estudio",
                    started_at=started,
                    ended_at=started + timedelta(minutes=minutes),
                )
            )
        user.total_focus_points = 120
        db.session.commit()


def test_overview_streak_and_series(app, client, auth):
    seed_sessions(app)
    body = client.get("/api/v1/stats/overview?days=7", headers=auth).get_json()
    overview = body["overview"]
    assert overview["total_sessions"] == 3
    assert overview["total_minutes"] == 120
    assert overview["current_streak"] == 3
    assert overview["today_minutes"] == 40
    assert len(body["daily"]) == 7
    assert body["tags"][0]["tag"] == "estudio"
    assert sum(hour["minutes"] for hour in body["hours"]) == 120


def test_daily_goal_progress(app, client, auth):
    seed_sessions(app)
    client.patch("/api/v1/users/me", headers=auth, json={"daily_goal_minutes": 80})
    overview = client.get("/api/v1/stats/overview", headers=auth).get_json()["overview"]
    assert overview["daily_goal_progress"] == 0.5


def test_leaderboard_marks_me(app, client, auth):
    seed_sessions(app)
    board = client.get("/api/v1/stats/leaderboard", headers=auth).get_json()["leaderboard"]
    assert board[0]["username"] == "eduardo"
    assert board[0]["is_me"] is True


def test_challenge_progress_updates_on_completion(app, client, auth):
    end_date = (utcnow() + timedelta(days=3)).isoformat()
    challenge = client.post(
        "/api/v1/challenges",
        headers=auth,
        json={"title": "Reto semanal", "metric": "minutes", "target_value": 20,
              "reward_points": 200, "end_date": end_date},
    ).get_json()
    join_url = f"/api/v1/challenges/{challenge['id']}/join"
    assert client.post(join_url, headers=auth).status_code == 201
    assert client.post(join_url, headers=auth).status_code == 409

    session_id = client.post(
        "/api/v1/sessions", headers=auth, json={"planned_minutes": 25}
    ).get_json()["id"]
    with app.app_context():
        session = db.session.get(FocusSession, session_id)
        session.started_at = utcnow() - timedelta(minutes=25)
        db.session.commit()
    body = client.post(f"/api/v1/sessions/{session_id}/complete", headers=auth).get_json()
    assert body["challenge_updates"][0]["completed"] is True
    assert body["challenge_updates"][0]["points_earned"] == 200


def test_blocked_app_check_during_session(client, auth):
    client.post(
        "/api/v1/blocked-apps",
        headers=auth,
        json={"app_name": "TikTok", "package_name": "com.zhiliaoapp.musically"},
    )
    payload = {"package_name": "com.zhiliaoapp.musically"}
    assert client.post("/api/v1/blocked-apps/check", headers=auth, json=payload).get_json() == {
        "blocked": False,
        "reason": None,
    }
    client.post("/api/v1/sessions", headers=auth, json={"planned_minutes": 25})
    assert client.post("/api/v1/blocked-apps/check", headers=auth, json=payload).get_json() == {
        "blocked": True,
        "reason": "focus_session",
    }
