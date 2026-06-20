import pytest

ARTICLE_PAYLOAD = {
    "name": "Veste en cuir noir",
    "description": "Veste courte en cuir véritable noir, col mao, fermeture éclair argent.",
    "price": 249.0, "brand": "TheKooples", "category_id": 1
}

@pytest.fixture
def category_id(client):
    cats = {c["slug"]: c["id"] for c in client.get("/categories/").json()}
    return cats["hauts"]
@pytest.fixture
def created_article(client, auth_headers, category_id):
    payload = {**ARTICLE_PAYLOAD, "category_id": category_id}
    resp = client.post("/articles/", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()

def test_get_articles_empty(client):
    assert client.get("/articles/").json()["total"] == 0
def test_create_article(client, auth_headers, category_id):
    resp = client.post("/articles/", headers=auth_headers,
        json={**ARTICLE_PAYLOAD, "category_id": category_id})
    assert resp.status_code == 201
    assert resp.json()["category"]["slug"] == "hauts"

def test_create_article_no_auth(client, category_id):
    resp = client.post("/articles/",
        json={**ARTICLE_PAYLOAD, "category_id": category_id})
    assert resp.status_code == 401

def test_get_article_not_found(client):
    assert client.get("/articles/9999").status_code == 404
def test_patch_article_price(client, auth_headers, created_article):
    resp = client.patch(f"/articles/{created_article['id']}",
        headers=auth_headers, json={"price": 199.0})
    assert resp.status_code == 200
    assert resp.json()["price"] == 199.0

def test_delete_article(client, auth_headers, created_article):
    aid = created_article["id"]
    assert client.delete(f"/articles/{aid}", headers=auth_headers).status_code == 204
    assert client.get(f"/articles/{aid}").status_code == 404
def test_get_stats(client, auth_headers, created_article):
    resp = client.get("/articles/stats")
    data = resp.json()
    assert data["total_articles"] >= 1
    assert "hauts" in data["by_category"]            