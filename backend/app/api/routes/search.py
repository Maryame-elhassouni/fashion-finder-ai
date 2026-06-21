import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from backend.app.core.database import get_db
from backend.app.core.security import get_optional_user, get_current_user

from backend.app.models.article import Article
from backend.app.models.category import Category
from backend.app.models.search_history import SearchHistory
from backend.app.models.user import User

from backend.app.schemas.search import (
    SearchRequest,
    SearchResponse,
    ArticleWithScore,
    SortBy
)

from backend.app.schemas.article import ArticleResponse
from backend.app.services.search_service import (
    extract_keywords,
    compute_relevance_score,
    score_to_label
)

from pydantic import BaseModel


router = APIRouter(prefix="/search", tags=["Recherche"])


# =========================
# 🔎 SEARCH ENDPOINT
# =========================
@router.post("/", response_model=SearchResponse)
def search_articles(
    data: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user)
):
    start_time = time.time()

    keywords = extract_keywords(data.description)

    query = db.query(Article).options(joinedload(Article.category))

    # =========================
    # CATEGORY FILTER
    # =========================
    if data.category_filter:
        cat = db.query(Category).filter(
            Category.slug == data.category_filter
        ).first()

        if not cat:
            raise HTTPException(status_code=400, detail="Category not found")

        query = query.filter(Article.category_id == cat.id)

    # =========================
    # PRICE FILTER
    # =========================
    if data.price_min is not None and data.price_max is not None:
        if data.price_min > data.price_max:
            raise HTTPException(status_code=400, detail="price_min > price_max")

    if data.price_min is not None:
        query = query.filter(Article.price >= data.price_min)

    if data.price_max is not None:
        query = query.filter(Article.price <= data.price_max)

    # =========================
    # KEYWORDS FILTER
    # =========================
    if keywords:
        conditions = [
            or_(
                Article.name.ilike(f"%{kw}%"),
                Article.description.ilike(f"%{kw}%")
            )
            for kw in keywords
        ]
        query = query.filter(or_(*conditions))

    all_articles = query.all()

    # =========================
    # SCORING
    # =========================
    scored = []
    for article in all_articles:
        score = compute_relevance_score(article, keywords)
        scored.append({
            "article": article,
            "score": score,
            "score_label": score_to_label(score)
        })

    total = len(scored)

    # =========================
    # SORT
    # =========================
    if data.sort_by == SortBy.relevance:
        scored.sort(key=lambda x: x["score"], reverse=True)
    elif data.sort_by == SortBy.price_asc:
        scored.sort(key=lambda x: x["article"].price)
    elif data.sort_by == SortBy.price_desc:
        scored.sort(key=lambda x: x["article"].price, reverse=True)
    elif data.sort_by == SortBy.newest:
        scored.sort(key=lambda x: x["article"].created_at, reverse=True)

    # =========================
    # PAGINATION
    # =========================
    total_pages = max(1, (total + data.size - 1) // data.size)
    offset = (data.page - 1) * data.size
    page_items = scored[offset: offset + data.size]

    results = [
        ArticleWithScore(
            article=ArticleResponse.model_validate(item["article"]),
            score=item["score"],
            score_label=item["score_label"]
        )
        for item in page_items
    ]

    duration_ms = int((time.time() - start_time) * 1000)

    # =========================
    # SAVE HISTORY
    # =========================
    if current_user:
        db.add(SearchHistory(
            user_id=current_user.id,
            description=data.description,
            category_filter=data.category_filter,
            results_count=total,
            duration_ms=duration_ms
        ))
        db.commit()

    return SearchResponse(
        description=data.description,
        total=total,
        page=data.page,
        size=data.size,
        total_pages=total_pages,
        results=results,
        search_type="keywords",
        duration_ms=duration_ms,
        filters_applied={
            "category": data.category_filter,
            "price_min": data.price_min,
            "price_max": data.price_max,
            "sort_by": data.sort_by
        }
    )


# =========================
# 📜 SEARCH HISTORY SCHEMA
# =========================
class SearchHistoryItem(BaseModel):
    id: int
    description: str
    category_filter: str | None
    results_count: int
    duration_ms: int | None
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# 📜 GET HISTORY ENDPOINT
# =========================
@router.get("/history", response_model=list[SearchHistoryItem])
def get_search_history(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
        .all()
    )