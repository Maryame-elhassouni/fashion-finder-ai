"""Tests unitaires des validateurs Pydantic — aucune BDD."""
import pytest
from pydantic import ValidationError
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.schemas.auth import UserRegister

BASE = {
    "name": "Veste Cuir Noir",
    "description": "Belle veste courte en cuir véritable noir avec fermeture éclair.",
    "price": 249.0,
    "category_id": 1
}
# ── ArticleCreate ─────────────────────────────────────────────────────────────
def test_name_stripped():
    a = ArticleCreate(**{**BASE, "name": "  Veste   Cuir  "})
    assert a.name == "Veste Cuir"

def test_price_rounded():
    a = ArticleCreate(**{**BASE, "price": 49.999})
    assert a.price == 50.0

def test_price_zero_rejected():
    with pytest.raises(ValidationError):
        ArticleCreate(**{**BASE, "price": 0})
def test_price_negative_rejected():
    with pytest.raises(ValidationError):
        ArticleCreate(**{**BASE, "price": -10})

def test_price_too_high_rejected():
    with pytest.raises(ValidationError):
        ArticleCreate(**{**BASE, "price": 15000})

def test_name_too_short():
    with pytest.raises(ValidationError):
        ArticleCreate(**{**BASE, "name": "X"})
def test_description_too_short():
    with pytest.raises(ValidationError):
        ArticleCreate(**{**BASE, "description": "Court"})

def test_valid_image_url():
    a = ArticleCreate(**{**BASE, "image_url": "https://example.com/photo.jpg"})
    assert a.image_url is not None

def test_invalid_image_url():
    with pytest.raises(ValidationError):
        ArticleCreate(**{**BASE, "image_url": "pas-une-url"})
def test_image_url_none_ok():
    a = ArticleCreate(**{**BASE, "image_url": None})
    assert a.image_url is None

def test_webp_url_accepted():
    a = ArticleCreate(**{**BASE, "image_url": "https://cdn.shop.com/img/p.webp"})
    assert a.image_url is not None

# ── ArticleUpdate ─────────────────────────────────────────────────────────────
def test_update_empty_returns_empty_dict():
    assert ArticleUpdate().to_update_dict() == {}                
def test_update_only_price():
    d = ArticleUpdate(price=99.0).to_update_dict()
    assert d == {"price": 99.0}
    assert "name" not in d

def test_update_price_rounded():
    assert ArticleUpdate(price=29.999).price == 30.0

# ── UserRegister ──────────────────────────────────────────────────────────────
def test_user_valid():
    u = UserRegister(email="t@t.com", full_name="Test", password="pass123")
    assert u.email == "t@t.com"
def test_user_invalid_email():
    with pytest.raises(ValidationError):
        UserRegister(email="pas-un-email", full_name="T", password="pass123")

def test_user_password_too_short():
    with pytest.raises(ValidationError):
        UserRegister(email="t@t.com", full_name="T", password="abc")        