"""
Tests des services IA — utilisent de vrais appels Gemini/embeddings.
Marqués 'slow' car ils font des appels réseau réels.
"""
import pytest
from app.services.embedding_service import generate_embedding
from app.services.ai_service import extract_attributes

@pytest.mark.slow
def test_generate_embedding_dimension():
    """L'embedding a la bonne dimension (384 pour ce modèle)."""
    vec = generate_embedding("veste noire")
    assert len(vec) == 384

@pytest.mark.slow
def test_generate_embedding_different_texts():
    """Deux textes différents donnent des embeddings différents."""
    v1 = generate_embedding("veste noire")
    v2 = generate_embedding("robe rouge")
    assert v1 != v2

@pytest.mark.slow
def test_extract_attributes_returns_dict(skip_if_no_gemini_key):
    """Gemini retourne bien un dict avec les bonnes clés."""
    result = extract_attributes("veste courte cuir noir fermeture éclair")
    assert "couleur" in result
    assert "categorie_slug" in result
    assert result["categorie_slug"] in {
        "hauts","bas","robes","vestes","chaussures","accessoires"
    }