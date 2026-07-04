import pytest


# =========================
# FIXTURE SEED ARTICLES
# =========================
@pytest.fixture
def seeded_articles(client, auth_headers):
    cats = {c["slug"]: c["id"] for c in client.get("/categories/").json()}

    articles = [
        {
            "name": "Veste cuir noir biker",
            "description": "Veste courte en cuir noir fermeture éclair argent style rock",
            "price": 249.0,
            "category_id": cats["vestes"]
        },
        {
            "name": "Robe fleurie midi",
            "description": "Robe longueur midi en viscose imprimé fleuri col V ceinture",
            "price": 72.0,
            "category_id": cats["robes"]
        },
        {
            "name": "Jean slim bleu indigo",
            "description": "Jean slim taille haute denim bleu indigo 5 poches fermeture",
            "price": 89.0,
            "category_id": cats["bas"]
        },
        {
            "name": "Pull col roulé camel",
            "description": "Pull doux laine mélangée col roulé coupe ajustée camel",
            "price": 79.9,
            "category_id": cats["hauts"]
        }
    ]

    for article in articles:
        resp = client.post(
            "/articles/",
            json=article,
            headers=auth_headers
        )
        assert resp.status_code in (200, 201)

    return True


# =========================
# SEARCH BASIC
# =========================
def test_search_finds_veste(client, seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={"description": "veste cuir noir"},
        headers=auth_headers
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["search_type"] == "ai"
    assert data["total"] >= 1
    assert len(data["results"]) >= 1


def test_search_finds_robe(client, seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={"description": "robe fleurie"},
        headers=auth_headers
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["search_type"] == "ai"
    assert data["total"] >= 1


# =========================
# CATEGORY FILTER
# =========================
def test_search_category_filter(client, seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={
            "description": "vêtement",
            "category_filter": "robes"
        },
        headers=auth_headers
    )

    assert resp.status_code == 200

    data = resp.json()

    for r in data["results"]:
        assert r["article"]["category"]["slug"] == "robes"


# =========================
# NO MATCH
# =========================
def test_search_no_match(client, seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={"description": "zzzinexistant999"},
        headers=auth_headers
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["search_type"] == "ai"
    assert "results" in data
    assert data["total"] >= 0


# =========================
# RESPONSE STRUCTURE
# =========================
def test_search_response_structure(client, seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={"description": "veste"},
        headers=auth_headers
    )

    assert resp.status_code == 200

    data = resp.json()

    assert "total" in data
    assert "results" in data
    assert "total_pages" in data
    assert "duration_ms" in data
    assert "search_type" in data

    assert data["search_type"] == "ai"

    for result in data["results"]:
        assert "article" in result
        assert "score" in result
        assert "score_label" in result

        article = result["article"]

        assert "id" in article
        assert "name" in article
        assert "description" in article
        assert "price" in article
        assert "category" in article
        assert "slug" in article["category"]


# =========================
# SHORT WORDS
# =========================
def test_search_short_words_ignored(client, seeded_articles, auth_headers):
    resp = client.post(
        "/search/",
        json={"description": "un de la"},
        headers=auth_headers
    )

    assert resp.status_code == 200

    data = resp.json()

    assert "results" in data


# =========================
# EMPTY DESCRIPTION
# =========================
def test_search_empty_description_fails(client, auth_headers):
    resp = client.post(
        "/search/",
        json={"description": ""},
        headers=auth_headers
    )

    assert resp.status_code in (400, 422)


# =========================
# PAGINATION
# =========================
def test_search_pagination(client, seeded_articles, auth_headers):
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
def test_history_after_search(client, seeded_articles, auth_headers):
    client.post(
        "/search/",
        json={"description": "veste"},
        headers=auth_headers
    )

    resp = client.get(
        "/search/history",
        headers=auth_headers
    )

    assert resp.status_code == 200

    data = resp.json()

    assert any(item["description"] == "veste" for item in data)