from backend.app.services.search_service import (
    extract_keywords, compute_relevance_score, score_to_label
)
from backend.app.models.article import Article

def make_article(name, description):
    return Article(
        name=name,
        description=description,
        price=10.0,
        category_id=1
    )
def test_extract_keywords_basic():
    kws = extract_keywords("veste cuir noir")
    assert "veste" in kws and "cuir" in kws
def test_extract_keywords_removes_stop_words():
    kws = extract_keywords("une veste de cuir avec des boutons")
    assert "une" not in kws and "des" not in kws

def test_extract_keywords_empty():
    assert extract_keywords("") == []

def test_score_keyword_in_name():
    a = make_article("Veste cuir noir", "Belle veste hiver")
    assert compute_relevance_score(a, ["veste"]) >= 0.4

def test_score_no_match():
    a = make_article("Robe fleurie", "Robe été coton")
    assert compute_relevance_score(a, ["veste","cuir"]) == 0.0
def test_score_capped_at_one():
    a = make_article("Veste cuir noir biker rock", "Veste cuir noir biker rock col")
    score = compute_relevance_score(a, ["veste","cuir","noir","biker","rock"])
    assert score <= 1.0

def test_score_empty_keywords():
    a = make_article("Veste", "Belle veste")
    assert compute_relevance_score(a, []) == 0.5

def test_label_excellent():
    assert score_to_label(0.9) == "Excellent"

def test_label_faible():
    assert score_to_label(0.0) == "Faible"        