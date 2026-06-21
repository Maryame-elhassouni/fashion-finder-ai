import pytest


# =========================
# SEARCH SCORE
# =========================
def test_search_has_score(client,seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={"description": "veste cuir noir"},
        headers=auth_headers
    )

    assert resp.status_code == 200

    data = resp.json()

    assert "total_pages" in data
    assert "duration_ms" in data
    assert "results" in data

    for r in data["results"]:
        assert 0.0 <= r["score"] <= 1.0
        assert "score_label" in r


# =========================
# SORT BY RELEVANCE
# =========================
def test_search_sorted_by_relevance(client, seeded, auth_headers):
    resp = client.post(
        "/search/",
        json={
            "description": "veste cuir noir",
            "sort_by": "relevance"
        },
        headers=auth_headers
    )

    assert resp.status_code == 200

    results = resp.json()["results"]
    scores = [r["score"] for r in results]

    assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))


# =========================
# PRICE FILTER
# =========================
def test_search_price_filter(client, seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={
            "description": "vêtement",
            "price_min": 50.0,
            "price_max": 150.0
        },
        headers=auth_headers
    )

    assert resp.status_code == 200

    for r in resp.json()["results"]:
        price = r["article"]["price"]
        assert 50.0 <= price <= 150.0


# =========================
# INVALID PRICE RANGE
# =========================
def test_search_invalid_price_range(client,seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={
            "description": "test",
            "price_min": 200.0,
            "price_max": 50.0
        },
        headers=auth_headers
    )

    assert resp.status_code == 400


# =========================
# INVALID CATEGORY
# =========================
def test_search_invalid_category(client, seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={
            "description": "test",
            "category_filter": "inexistante"
        },
        headers=auth_headers
    )

    assert resp.status_code == 400


# =========================
# PAGINATION
# =========================
def test_search_pagination(client,seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={
            "description": "mode",
            "page": 1,
            "size": 2
        },
        headers=auth_headers
    )

    assert resp.status_code == 200

    data = resp.json()
    assert len(data["results"]) <= 2
    assert "total_pages" in data


# =========================
# HISTORY AUTH REQUIRED
# =========================
def test_history_requires_auth(client):
    resp = client.get("/search/history")
    assert resp.status_code == 401


# =========================
# HISTORY AFTER SEARCH
# =========================
def test_history_after_search(client,seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={"description": "veste"},
        headers=auth_headers
    )
    assert resp.status_code == 200

    resp = client.get(
        "/search/history",
        headers=auth_headers
    )
    assert resp.status_code == 200

    data = resp.json()
    assert any(item["description"] == "veste" for item in data)