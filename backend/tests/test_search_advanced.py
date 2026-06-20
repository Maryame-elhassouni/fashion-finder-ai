import pytest

@pytest.fixture
def seeded_articles(client, auth_headers):
    cats = {c["slug"]: c["id"] for c in client.get("/categories/").json()}
    data = [
        {"name":"Veste cuir noir biker",  "description":"Veste courte en cuir noir fermeture éclair argent style rock.","price":249.0,"category_id":cats["vestes"]},
        {"name":"Robe fleurie midi",       "description":"Robe longueur midi en viscose imprimé fleuri col V ceinture.","price":72.0, "category_id":cats["robes"]},
        {"name":"Jean slim bleu indigo",   "description":"Jean slim taille haute denim bleu indigo 5 poches fermeture.","price":89.0, "category_id":cats["bas"]},
        {"name":"Pull col roulé camel",    "description":"Pull doux laine mélangée col roulé coupe ajustée coloris camel.","price":79.9,"category_id":cats["hauts"]},
    ]
    for a in data:
        client.post("/articles/", headers=auth_headers, json=a)
def test_search_finds_veste(client, seeded_articles):
    resp = client.post("/search/", json={"description":"veste cuir noir"})
    assert resp.json()["total"] >= 1

def test_search_finds_robe(client, seeded_articles):
    resp = client.post("/search/", json={"description":"robe fleurie"})
    assert resp.json()["total"] >= 1

def test_search_category_filter(client, seeded_articles):
    """Filtre catégorie — uniquement des robes."""
    resp = client.post("/search/", json={
        "description":"vêtement","category_filter":"robes"
    })
    assert resp.status_code == 200
    for r in resp.json()["results"]:
        assert r["category"]["slug"] == "robes"

def test_search_no_match(client, seeded_articles):
    resp = client.post("/search/", json={"description":"zzzinexistant999"})
    assert resp.json()["total"] == 0

def test_search_response_structure(client, seeded_articles):
    """La réponse a tous les champs requis."""
    data = client.post("/search/", json={"description":"veste"}).json()
    assert "total" in data
    assert "results" in data
    assert "description" in data
    assert "search_type" in data
    assert data["search_type"] == "keywords"
def test_search_short_words_ignored(client, seeded_articles):
    """Mots de moins de 3 chars ignorés — pas d'erreur."""
    resp = client.post("/search/", json={"description":"un de la"})
    assert resp.status_code == 200

def test_search_empty_description_fails(client):
    resp = client.post("/search/", json={"description":""})
    assert resp.status_code == 422            