import pytest

@pytest.fixture
def article(client, auth_headers):
    cats = {c["slug"]: c["id"] for c in client.get("/categories/").json()}
    resp = client.post("/articles/", headers=auth_headers, json={
        "name": "Veste Cuir Noir",
        "description": "Veste courte en cuir véritable noir, fermeture éclair argent.",
        "price": 249.0, "category_id": cats["vestes"]
    })
    return resp.json()

def test_patch_price(client, auth_headers, article):
    resp = client.patch(f"/articles/{article['id']}", headers=auth_headers,
        json={"price": 199.0})
    assert resp.status_code == 200
    assert resp.json()["price"] == 199.0
    assert resp.json()["name"] == "Veste Cuir Noir"
def test_patch_name_cleaned(client, auth_headers, article):
    resp = client.patch(f"/articles/{article['id']}", headers=auth_headers,
        json={"name": "  Veste   Modifiée  "})
    assert resp.json()["name"] == "Veste Modifiée"

def test_patch_empty_body(client, auth_headers, article):
    resp = client.patch(f"/articles/{article['id']}", headers=auth_headers, json={})
    assert resp.status_code == 400

def test_patch_not_found(client, auth_headers):
    resp = client.patch("/articles/9999", headers=auth_headers, json={"price": 50.0})
    assert resp.status_code == 404

def test_patch_without_auth(client, article):
    resp = client.patch(f"/articles/{article['id']}", json={"price": 50.0})
    assert resp.status_code == 401
def test_patch_invalid_price(client, auth_headers, article):
    resp = client.patch(f"/articles/{article['id']}", headers=auth_headers,
        json={"price": -10.0})
    assert resp.status_code == 422

def test_patch_wrong_category(client, auth_headers, article):
    resp = client.patch(f"/articles/{article['id']}", headers=auth_headers,
        json={"category_id": 9999})
    assert resp.status_code == 404

def test_get_stats_empty(client):
    resp = client.get("/articles/stats")
    assert resp.json()["total_articles"] == 0

def test_get_stats_with_articles(client, auth_headers, article):
    data = client.get("/articles/stats").json()
    assert data["total_articles"] >= 1
    assert data["avg_price"] > 0
    assert "vestes" in data["by_category"]        