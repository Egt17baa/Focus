import pytest

from focus import create_app
from focus.config import TestConfig
from focus.extensions import db


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth(client):
    """Registra un usuario y devuelve headers autenticados."""
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "eduardo", "email": "eduardo@example.com", "password": "focus1234"},
    )
    assert response.status_code == 201, response.get_json()
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
