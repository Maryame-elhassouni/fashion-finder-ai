import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.models.category import Category

# SQLite en mémoire pour les tests — pas PostgreSQL
TEST_DB = "sqlite:///./test.db"
engine_test = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    from backend.app.main import app  # force le chargement de tous les modèles
    from backend.app.core.database import Base

    # Nettoyer d'abord
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    from backend.app.models.category import Category
    db = TestingSession()
    try:
        for cat in [
            Category(name="Hauts",       slug="hauts",       icon_emoji="👕"),
            Category(name="Robes",       slug="robes",       icon_emoji="👗"),
            Category(name="Vestes",      slug="vestes",      icon_emoji="🧥"),
            Category(name="Bas",         slug="bas",         icon_emoji="👖"),
            Category(name="Chaussures",  slug="chaussures",  icon_emoji="👟"),
            Category(name="Accessoires", slug="accessoires", icon_emoji="👜"),
        ]:
            db.add(cat)
        db.commit()
    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=engine_test)

@pytest.fixture
def client():
    return TestClient(app)

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
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}