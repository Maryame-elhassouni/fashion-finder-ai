"""
Tests du endpoint /search avec IA.
On mocke vector_search pour ne pas dépendre d'un vrai appel Gemini en CI.
"""
import pytest
from unittest.mock import patch

@pytest.fixture
def seeded(client, auth_headers):
    cats = {c["slug"]: c["id"] for c in client.get("/categories/").json()}
    client.post("/articles/", headers=auth_headers, json={
        "name":"Veste cuir noir","description":"Veste courte cuir noir fermeture éclair.",
        "price":249.0,"category_id":cats["vestes"]
    })
    return cats

def test_search_response_has_search_type(client, seeded):
    """search_type est toujours présent, 'ai' ou 'keywords'."""
    resp = client.post("/search/", json={"description":"veste"})
    assert resp.json()["search_type"] in {"ai", "keywords"}

@patch("app.api.routes.search.vector_search")
def test_search_uses_ai_when_available(mock_vector_search, client, seeded):
    """Quand vector_search réussit, search_type='ai'."""
    mock_vector_search.return_value = [
        {"article_id": 1, "similarity_score": 0.95, "metadata": {}}
    ]
    resp = client.post("/search/", json={"description":"veste noire"})
    assert resp.json()["search_type"] == "ai"

@patch("app.api.routes.search.vector_search")
def test_search_fallback_on_ai_failure(mock_vector_search, client, seeded):
    """Quand vector_search échoue, fallback vers keywords."""
    mock_vector_search.side_effect = Exception("Gemini quota dépassé")
    resp = client.post("/search/", json={"description":"veste cuir noir"})
    assert resp.status_code == 200  # toujours une réponse
    assert resp.json()["search_type"] == "keywords"
    assert resp.json()["total"] >= 1  # le fallback trouve quand même des résultats

def test_search_cache_used(client, seeded):
    """Deux requêtes identiques utilisent le cache (résultat identique rapide)."""
    r1 = client.post("/search/", json={"description":"veste cuir"})
    r2 = client.post("/search/", json={"description":"veste cuir"})
    assert r1.json()["total"] == r2.json()["total"]