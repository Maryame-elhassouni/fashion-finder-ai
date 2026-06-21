import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.models.category import Category

from backend.seed_articles import seed_articles  # ⚠️ IMPORTANT: import module, pas variable

# =========================
# DB TEST
# =========================
TEST_DB = "sqlite:///./test.db"
engine_test = create_engine(
    TEST_DB,
    connect_args={"check_same_thread": False}
)

TestingSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)

# =========================
# OVERRIDE DB
# =========================
def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# =========================
# SETUP DB (CATEGORIES ONLY)
# =========================
@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    db = TestingSession()
    try:
        cats = [
            Category(name="Hauts", slug="hauts", icon_emoji="👕"),
            Category(name="Robes", slug="robes", icon_emoji="👗"),
            Category(name="Vestes", slug="vestes", icon_emoji="🧥"),
            Category(name="Bas", slug="bas", icon_emoji="👖"),
            Category(name="Chaussures", slug="chaussures", icon_emoji="👟"),
            Category(name="Accessoires", slug="accessoires", icon_emoji="👜"),
        ]
        db.add_all(cats)
        db.commit()
    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=engine_test)

# =========================
# CLIENT
# =========================
@pytest.fixture
def client():
    return TestClient(app)

# =========================
# AUTH
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

    return {
        "Authorization": f"Bearer {resp.json()['access_token']}"
    }

# =========================
# ARTICLES SEED FIX (IMPORTANT)
# =========================
@pytest.fixture
def seeded_articles():
    

    seed_articles   # 👈 TU DOIS avoir une fonction seed(db)

    yield

# =========================
# FIX FINAL SEED
# =========================
@pytest.fixture
def seeded(seeded_articles, auth_headers):
    return {
        "ok": True,
        "auth_headers": auth_headers
    }