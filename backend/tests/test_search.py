import pytest

@pytest.fixture
def seeded(client, auth_headers):
    cats = {c["slug"]: c["id"] for c in client.get("/categories/").json()}
    client.post("/articles/", headers=auth_headers, json={
        "name":"Veste cuir noir biker","description":"Veste courte en cuir noir, fermeture éclair argent.",
        "price":249.0,"category_id":cats["vestes"]
    })
def test_search_returns_results(client, seeded):
    resp = client.post("/search/", json={"description": "veste cuir noir"})
    assert resp.json()["total"] >= 1

def test_search_with_category(client, seeded):
    resp = client.post("/search/", json={
        "description": "veste", "category_filter": "vestes"
    })
    for r in resp.json()["results"]:
        assert r["category"]["slug"] == "vestes"
def test_search_no_match(client, seeded):
    resp = client.post("/search/", json={"description": "zzzinexistant"})
    assert resp.json()["total"] == 0