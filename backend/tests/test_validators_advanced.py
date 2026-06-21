import pytest
from pydantic import ValidationError
from backend.app.schemas.article import ArticleCreate, ArticleUpdate

BASE = {
    "name": "Veste en Cuir Noir",
    "description": "Belle veste courte en cuir véritable noir avec fermeture éclair.",
    "price": 249.0, "category_id": 1
}

def test_name_with_extra_spaces():
    a = ArticleCreate(**{**BASE, "name": "  Veste   Cuir  "})
    assert a.name == "Veste Cuir"

def test_description_same_as_name_rejected():
    with pytest.raises(ValidationError):
        ArticleCreate(
            **{
                **BASE,
                "name": "veste",
                "description": "veste"
            }
        )
def test_update_to_dict_excludes_none():
    d = ArticleUpdate(price=99.0).to_update_dict()
    assert "name" not in d
    assert d["price"] == 99.0

def test_update_empty():
    assert ArticleUpdate().to_update_dict() == {}