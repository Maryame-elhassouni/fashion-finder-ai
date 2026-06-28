import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.category import Category
from seed_articles import seed_articles


# =========================
# TEST DATABASE
# =========================
TEST_DB_URL = "sqlite:///./test.db"

engine_test = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)


# =========================
# OVERRIDE DB DEPENDENCY
# =========================
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# =========================
# SETUP DATABASE (CLEAN EACH TEST)
# =========================
@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    db = TestingSessionLocal()
    try:
        categories = [
            Category(name="Hauts", slug="hauts", icon_emoji="👕"),
            Category(name="Robes", slug="robes", icon_emoji="👗"),
            Category(name="Vestes", slug="vestes", icon_emoji="🧥"),
            Category(name="Bas", slug="bas", icon_emoji="👖"),
            Category(name="Chaussures", slug="chaussures", icon_emoji="👟"),
            Category(name="Accessoires", slug="accessoires", icon_emoji="👜"),
        ]
        db.add_all(categories)
        db.commit()
    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=engine_test)


# =========================
# TEST CLIENT
# =========================
@pytest.fixture
def client():
    return TestClient(app)


# =========================
# AUTH FIXTURE
# =========================
@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "email": "test@fashion.com",
        "full_name": "Test User",
        "password": "testpass123"
    })

    resp = client.post("/auth/login", json={
        "email": "test@fashion.com",
        "password": "testpass123"
    })

    token = resp.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# =========================
# CATEGORY IDS FIXTURE
# =========================
@pytest.fixture
def cat_ids(client):
    resp = client.get("/categories/")
    return {c["slug"]: c["id"] for c in resp.json()}


# =========================
# ARTICLE FIXTURE (IMPORTANT)
# =========================
@pytest.fixture
def article(client, auth_headers, cat_ids):
    resp = client.post("/articles/", headers=auth_headers, json={
        "name": "Veste Test",
        "description": "Article test",
        "price": 120,
        "brand": "TestBrand",
        "category_id": cat_ids["vestes"]
    })

    assert resp.status_code == 201
    return resp.json()


# =========================
# OPTIONAL SEED (if needed)
# =========================
@pytest.fixture
def seeded_articles():
    db = TestingSessionLocal()
    try:
        seed_articles(db)
    finally:
        db.close()


@pytest.fixture
def seeded(seeded_articles, auth_headers):
    return {
        "auth_headers": auth_headers
    }

@pytest.fixture
def skip_if_no_gemini_key():
    if not os.environ.get("GEMINI_API_KEY") or "fake" in os.environ.get("GEMINI_API_KEY", ""):
        pytest.skip("Pas de vraie clé Gemini disponible")