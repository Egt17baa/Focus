from datetime import timedelta

from focus.extensions import db
from focus.models import FocusSession, User, utcnow


def start(client, auth, **payload):
    return client.post("/api/v1/sessions", headers=auth, json={"planned_minutes": 25, **payload})


def backdate(app, session_id: int, minutes: int):
    """Simula que la sesión empezó hace N minutos."""
    with app.app_context():
        session = db.session.get(FocusSession, session_id)
        session.started_at = utcnow() - timedelta(minutes=minutes)
        db.session.commit()


def test_single_active_session(client, auth):
    assert start(client, auth).status_code == 201
    assert start(client, auth).status_code == 409


def test_active_endpoint(client, auth):
    assert client.get("/api/v1/sessions/active", headers=auth).get_json()["session"] is None
    start(client, auth)
    assert client.get("/api/v1/sessions/active", headers=auth).get_json()["session"] is not None


def test_invalid_mode_and_duration(client, auth):
    assert start(client, auth, mode="siesta").status_code == 400
    assert start(client, auth, planned_minutes=999).status_code == 400


def test_complete_awards_points_and_achievement(app, client, auth):
    session_id = start(client, auth, planned_minutes=30, tag="estudio").get_json()["id"]
    backdate(app, session_id, 30)

    body = client.post(f"/api/v1/sessions/{session_id}/complete", headers=auth).get_json()
    assert body["session"]["focus_minutes"] == 30
    # 30 min + bonus 25min (5) + bonus objetivo (10) = 45
    assert body["session"]["points_earned"] == 45
    codes = {a["achievement"]["code"] for a in body["unlocked_achievements"]}
    assert {"first_session", "streak_3"} & codes == {"first_session"}
    assert body["user"]["total_focus_points"] == 45 + 50


def test_pause_penalises_and_pauses_clock(app, client, auth):
    session_id = start(client, auth, planned_minutes=10).get_json()["id"]
    backdate(app, session_id, 10)
    assert client.post(f"/api/v1/sessions/{session_id}/pause", headers=auth).status_code == 200
    assert client.post(f"/api/v1/sessions/{session_id}/pause", headers=auth).status_code == 409
    assert client.post(f"/api/v1/sessions/{session_id}/resume", headers=auth).status_code == 200

    body = client.post(f"/api/v1/sessions/{session_id}/complete", headers=auth).get_json()
    # 10 minutos - 2 puntos por la interrupción + 10 de bonus por cumplir el objetivo
    assert body["session"]["interruptions"] == 1
    assert body["session"]["points_earned"] == 18


def test_abandon_gives_no_points(app, client, auth):
    session_id = start(client, auth).get_json()["id"]
    backdate(app, session_id, 5)
    body = client.post(f"/api/v1/sessions/{session_id}/abandon", headers=auth).get_json()
    assert body["status"] == "abandoned"
    assert body["points_earned"] == 0
    assert client.get("/api/v1/users/me", headers=auth).get_json()["total_focus_points"] == 0


def test_delete_completed_session_refunds_points(app, client, auth):
    session_id = start(client, auth).get_json()["id"]
    backdate(app, session_id, 25)
    client.post(f"/api/v1/sessions/{session_id}/complete", headers=auth)
    points_before = client.get("/api/v1/users/me", headers=auth).get_json()["total_focus_points"]

    client.delete(f"/api/v1/sessions/{session_id}", headers=auth)
    points_after = client.get("/api/v1/users/me", headers=auth).get_json()["total_focus_points"]
    assert points_after == points_before - 40


def test_sessions_are_scoped_to_owner(app, client, auth):
    session_id = start(client, auth).get_json()["id"]
    other = client.post(
        "/api/v1/auth/register",
        json={"username": "intrusa", "email": "i@example.com", "password": "focus1234"},
    ).get_json()
    headers = {"Authorization": f"Bearer {other['access_token']}"}
    response = client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)
    assert response.status_code == 404


def test_level_up_with_points(app, client, auth):
    with app.app_context():
        user = User.query.filter_by(username="eduardo").first()
        user.total_focus_points = 5200
        db.session.commit()
    me = client.get("/api/v1/users/me", headers=auth).get_json()
    assert me["level_name"] == "Maestro del Enfoque"
    assert 0 < me["level_progress"] < 1
