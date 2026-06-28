"""Tests unitaires de app/core/security.py — aucune BDD nécessaire."""
from app.core.security import (
    hash_password, verify_password,
    create_access_token, decode_token
)

# ── Hashing ───────────────────────────────────────────────────────────────────
def test_hash_not_plaintext():
    """Le hash ne contient pas le mot de passe en clair."""
    assert "monpass" not in hash_password("monpass")
def test_hash_different_each_time():
    """bcrypt génère un salt unique — deux hashes différents pour le même mdp."""
    assert hash_password("same") != hash_password("same")

def test_verify_correct():
    h = hash_password("correct")
    assert verify_password("correct", h) is True

def test_verify_wrong():
    h = hash_password("correct")
    assert verify_password("mauvais", h) is False
def test_verify_empty():
    assert verify_password("", hash_password("correct")) is False

# ── JWT ───────────────────────────────────────────────────────────────────────
def test_token_returns_string():
    t = create_access_token({"sub": "test@mode.com"})
    assert isinstance(t, str) and len(t) > 20

def test_token_starts_eyj():
    """Tous les JWT commencent par eyJ (base64 de '{')."""
    assert create_access_token({"sub": "u@t.com"}).startswith("eyJ")
def test_decode_valid():
    t = create_access_token({"sub": "u@t.com", "id": 42})
    d = decode_token(t)
    assert d is not None
    assert d["sub"] == "u@t.com"
    assert d["id"] == 42

def test_decode_invalid():
    assert decode_token("faux.token.invalide") is None

def test_decode_empty():
    assert decode_token("") is None
def test_decode_preserves_claims():
    t = create_access_token({"sub": "u@t.com", "role": "admin"})
    d = decode_token(t)
    assert d["role"] == "admin"    
