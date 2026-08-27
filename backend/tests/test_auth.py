def test_health(client):
    assert client.get("/api/v1/health").get_json()["status"] == "ok"


def test_register_validates_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "eduardo", "email": "e@example.com", "password": "short"},
    )
    assert response.status_code == 400


def test_register_rejects_duplicates(client, auth):
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "eduardo", "email": "otro@example.com", "password": "focus1234"},
    )
    assert response.status_code == 409


def test_login_and_me(client, auth):
    login = client.post(
        "/api/v1/auth/login", json={"username": "eduardo", "password": "focus1234"}
    )
    assert login.status_code == 200
    me = client.get("/api/v1/users/me", headers=auth)
    assert me.get_json()["username"] == "eduardo"
    assert me.get_json()["level_name"] == "Novato"


def test_login_with_bad_password(client, auth):
    response = client.post(
        "/api/v1/auth/login", json={"username": "eduardo", "password": "incorrecta"}
    )
    assert response.status_code == 401


def test_logout_revokes_token(client, auth):
    assert client.post("/api/v1/auth/logout", headers=auth).status_code == 200
    assert client.get("/api/v1/users/me", headers=auth).status_code == 401


def test_protected_route_requires_token(client):
    assert client.get("/api/v1/users/me").status_code == 401
