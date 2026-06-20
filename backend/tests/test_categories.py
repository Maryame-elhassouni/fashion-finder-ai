def test_get_categories_six(client):
    """GET /categories retourne exactement 6 catégories."""
    resp = client.get("/categories/")
    assert resp.status_code == 200
    assert len(resp.json()) == 6

def test_categories_have_fields(client):
    """Chaque catégorie a id, name, slug, icon_emoji."""
    for cat in client.get("/categories/").json():
        assert "id" in cat
        assert "name" in cat
        assert "slug" in cat
        assert "icon_emoji" in cat
def test_categories_slugs(client):
    """Les 6 slugs attendus sont tous présents."""
    slugs = {c["slug"] for c in client.get("/categories/").json()}
    assert slugs == {"hauts","bas","robes","vestes","chaussures","accessoires"}

def test_stats_empty(client):
    """Stats sur catalogue vide."""
    resp = client.get("/articles/stats")
    assert resp.status_code == 200
    assert resp.json()["total_articles"] == 0
def test_stats_with_article(client, auth_headers):
    cats = {c["slug"]: c["id"] for c in client.get("/categories/").json()}
    client.post("/articles/", headers=auth_headers, json={
        "name":"Test stat","description":"Description longue pour test statistique.",
        "price":99.0,"category_id":cats["hauts"]
    })
    data = client.get("/articles/stats").json()
    assert data["total_articles"] >= 1
    assert data["avg_price"] > 0
    assert data["min_price"] <= data["max_price"]            