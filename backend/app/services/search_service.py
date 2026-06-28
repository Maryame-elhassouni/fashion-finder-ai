from app.models.article import Article

def extract_keywords(description: str) -> list[str]:
    stop_words = {
        "de","du","des","le","la","les","un","une","en","et","ou",
        "avec","pour","sur","dans","par","qui","que","est","son","sa"
    }
    words = description.lower().split()
    
    return [
        w.strip(".,!?;:") for w in words
        if len(w) > 2 and w not in stop_words
    ][:8]
def compute_relevance_score(article: Article, keywords: list[str]) -> float:
    if not keywords:
        return 0.5
    score = 0.0
    name_lower = article.name.lower()
    desc_lower = article.description.lower()
    for kw in keywords:
        kw = kw.lower()
        if kw in name_lower:
            score += 0.4
        elif kw in desc_lower:
            score += 0.2
    return min(round(score, 2), 1.0)
def score_to_label(score: float) -> str:
    if score >= 0.8: return "Excellent"
    if score >= 0.5: return "Bon"
    if score >= 0.2: return "Moyen"
    return "Faible"