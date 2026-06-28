import pytest

BASE = {
    "name": "Veste Cuir",
    "description": "Veste courte en cuir véritable noir fermeture éclair.",
    "price": 249.0,
    "brand": "TheKooples"
}

@pytest.fixture
def cat_ids(client):
    return {c["slug"]: c["id"] for c in client.get("/categories/").json()}


# =========================
# PAGINATION
# =========================
def test_pagination_size(client, auth_headers, cat_ids):
    for i in range(3):
        client.post("/articles/", headers=auth_headers,
            json={**BASE, "name": f"Art {i}", "category_id": cat_ids["hauts"]})

    resp = client.get("/articles/?page=1&size=2")
    assert resp.json()["total"] == 3
    assert len(resp.json()["articles"]) == 2


def test_pagination_page2(client, auth_headers, cat_ids):
    for i in range(3):
        client.post("/articles/", headers=auth_headers,
            json={**BASE, "name": f"Art {i}", "category_id": cat_ids["hauts"]})

    resp = client.get("/articles/?page=2&size=2")
    assert len(resp.json()["articles"]) == 1


# =========================
# FILTER
# =========================
def test_filter_by_category(client, auth_headers, cat_ids):
    client.post("/articles/", headers=auth_headers,
        json={**BASE, "category_id": cat_ids["vestes"]})

    resp = client.get("/articles/category/vestes")

    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    for a in resp.json()["articles"]:
        assert a["category"]["slug"] == "vestes"


# =========================
# FIXTURE ARTICLE (IMPORTANT)
# =========================
@pytest.fixture
def article(client, auth_headers, cat_ids):
    resp = client.post("/articles/", headers=auth_headers, json={
        "name": "Veste Test",
        "description": "Test article",
        "price": 120,
        "brand": "TestBrand",
        "category_id": cat_ids["vestes"]
    })

    assert resp.status_code == 201
    return resp.json()


# =========================
# PATCH TESTS
# =========================
def test_patch_name_cleaned(client, auth_headers, article):
    resp = client.patch(f"/articles/{article['id']}", headers=auth_headers,
        json={"name": "  Veste   Modifiée  "})

    assert resp.json()["name"] == "Veste Modifiée"


def test_patch_wrong_category(client, auth_headers, article):
    resp = client.patch(f"/articles/{article['id']}", headers=auth_headers,
        json={"category_id": 9999})

    assert resp.status_code == 404


def test_patch_empty_body(client, auth_headers, article):
    resp = client.patch(f"/articles/{article['id']}", headers=auth_headers,
        json={})

    assert resp.status_code == 400


def test_patch_invalid_price(client, auth_headers, article):
    resp = client.patch(f"/articles/{article['id']}", headers=auth_headers,
        json={"price": -5})

    assert resp.status_code == 422


def test_patch_without_auth(client, article):
    resp = client.patch(f"/articles/{article['id']}",
        json={"price": 50})

    assert resp.status_code == 401


# =========================
# DELETE TESTS
# =========================
def test_delete_not_found(client, auth_headers):
    assert client.delete("/articles/9999", headers=auth_headers).status_code == 404


def test_delete_without_auth(client, article):
    assert client.delete(f"/articles/{article['id']}").status_code == 401