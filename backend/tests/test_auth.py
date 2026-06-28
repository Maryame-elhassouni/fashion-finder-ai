def test_register_success(client):
    resp = client.post("/auth/register", json={
        "email": "new@mode.com", "full_name": "New User", "password": "pass123"
    })
    assert resp.status_code == 201
    assert "access_token" in resp.json()
    assert resp.json()["user"]["email"] == "new@mode.com"
def test_register_duplicate_email(client):
    data = {"email": "dup@mode.com", "full_name": "Dup", "password": "pass123"}
    client.post("/auth/register", json=data)
    assert client.post("/auth/register", json=data).status_code == 400

def test_login_success(client):
    # Register
    r = client.post("/auth/register", json={
        "email": "login@mode.com", "full_name": "LAYLA", "password": "pass123"
    })
    # Vérifier que le register a réussi avant de tenter le login
    assert r.status_code == 201, f"Register failed: {r.json()}"

    resp = client.post("/auth/login", json={
        "email": "login@mode.com", "password": "pass123"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()
def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "email": "bad@mode.com", "full_name": "B", "password": "correct"
    })
    assert client.post("/auth/login", json={
        "email": "bad@mode.com", "password": "mauvais"
    }).status_code == 401

def test_get_me(client, auth_headers):
    resp = client.get("/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@fashion.com"

def test_get_me_no_token(client):
    assert client.get("/users/me").status_code == 401        