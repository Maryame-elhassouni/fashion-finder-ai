import os
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_optional_user, get_current_user
from app.core.simple_cache import (
    make_cache_key,
    cache_get,
    cache_set,
)

from app.models.article import Article
from app.models.category import Category
from app.models.search_history import SearchHistory
from app.models.user import User

from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    ArticleWithScore,
)

from app.schemas.article import ArticleResponse

from app.services.search_service import (
    extract_keywords,
    compute_relevance_score,
    score_to_label,
)

from app.services.vector_search_service import vector_search


router = APIRouter(
    prefix="/search",
    tags=["Recherche"],
)


@router.post("/", response_model=SearchResponse)
def search_articles(
    data: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    start_time = time.time()

    # ---------------- Validation ----------------

    if (
        data.price_min is not None
        and data.price_max is not None
        and data.price_min > data.price_max
    ):
        raise HTTPException(
            status_code=400,
            detail="price_min must be <= price_max",
        )

    search_type = "ai"
    ai_results = []

    # ---------------- Cache ----------------

    cache_key = make_cache_key(
        "search",
        data.description,
        data.category_filter,
        data.price_min,
        data.price_max,
        data.sort_by,
    )

    cached = None

    # Désactiver le cache pendant pytest
    if "PYTEST_CURRENT_TEST" not in os.environ:
        cached = cache_get(cache_key)

    if cached is not None:
        ai_results = cached

    else:

        try:

            category_id = None

            if data.category_filter:
                cat = (
                    db.query(Category)
                    .filter(Category.slug == data.category_filter)
                    .first()
                )

                if not cat:
                    raise HTTPException(
                        status_code=400,
                        detail="Catégorie introuvable",
                    )

                category_id = cat.id

            ai_results = vector_search(
                description=data.description,
                category_id=category_id,
                n_results=50,
            )

            if "PYTEST_CURRENT_TEST" not in os.environ:
                cache_set(cache_key, ai_results)

        except HTTPException:
            raise

        except Exception as e:
            print(f"[Search] IA indisponible : {e}")

            search_type = "keywords"
            ai_results = []

    # ==========================================================
    # RECHERCHE VECTORIELLE
    # ==========================================================

    if search_type == "ai" and ai_results:

        article_ids = [
            r["article_id"]
            for r in ai_results
        ]

        score_map = {
            r["article_id"]: r["similarity_score"]
            for r in ai_results
        }

        articles_db = (
            db.query(Article)
            .options(joinedload(Article.category))
            .filter(Article.id.in_(article_ids))
            .all()
        )

        # Conserver l'ordre renvoyé par ChromaDB
        articles_map = {
            article.id: article
            for article in articles_db
        }

        articles = [
            articles_map[id_]
            for id_ in article_ids
            if id_ in articles_map
        ]

        # ---------- Filtre catégorie ----------

        if data.category_filter:
            articles = [
                article
                for article in articles
                if article.category
                and article.category.slug == data.category_filter
            ]

        # ---------- Filtre prix ----------

        if data.price_min is not None:
            articles = [
                article
                for article in articles
                if article.price >= data.price_min
            ]

        if data.price_max is not None:
            articles = [
                article
                for article in articles
                if article.price <= data.price_max
            ]

        scored = []

        for article in articles:

            score = score_map.get(article.id, 0.0)

            if score > 0:

                scored.append(
                    {
                        "article": article,
                        "score": score,
                        "score_label": score_to_label(score),
                    }
                )

        scored.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

    else:
                # ==========================================================
        # FALLBACK RECHERCHE PAR MOTS-CLÉS
        # ==========================================================

        search_type = "keywords"

        keywords = extract_keywords(data.description)

        query = (
            db.query(Article)
            .options(joinedload(Article.category))
        )

        if data.category_filter:

            cat = (
                db.query(Category)
                .filter(Category.slug == data.category_filter)
                .first()
            )

            if not cat:
                raise HTTPException(
                    status_code=400,
                    detail="Catégorie introuvable",
                )

            query = query.filter(
                Article.category_id == cat.id
            )

        if data.price_min is not None:
            query = query.filter(
                Article.price >= data.price_min
            )

        if data.price_max is not None:
            query = query.filter(
                Article.price <= data.price_max
            )

        if keywords:

            conditions = [
                or_(
                    Article.name.ilike(f"%{kw}%"),
                    Article.description.ilike(f"%{kw}%"),
                )
                for kw in keywords
            ]

            query = query.filter(or_(*conditions))

        all_articles = query.all()

        scored = []

        for article in all_articles:

            score = compute_relevance_score(
                article,
                keywords,
            )

            if score > 0:

                scored.append(
                    {
                        "article": article,
                        "score": score,
                        "score_label": score_to_label(score),
                    }
                )

        scored.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

    # ==========================================================
    # PAGINATION
    # ==========================================================

    total = len(scored)

    total_pages = max(
        1,
        (total + data.size - 1) // data.size,
    )

    offset = (data.page - 1) * data.size

    page_items = scored[offset: offset + data.size]

    results = [
        ArticleWithScore(
            article=ArticleResponse.model_validate(
                item["article"]
            ),
            score=item["score"],
            score_label=item["score_label"],
        )
        for item in page_items
    ]

    duration_ms = int(
        (time.time() - start_time) * 1000
    )

    # ==========================================================
    # HISTORIQUE
    # ==========================================================

    if current_user:

        db.add(
            SearchHistory(
                user_id=current_user.id,
                description=data.description,
                category_filter=data.category_filter,
                results_count=total,
                duration_ms=duration_ms,
            )
        )

        db.commit()

    return SearchResponse(
        description=data.description,
        total=total,
        page=data.page,
        size=data.size,
        total_pages=total_pages,
        results=results,
        search_type=search_type,
        duration_ms=duration_ms,
        filters_applied={
            "category": data.category_filter,
            "price_min": data.price_min,
            "price_max": data.price_max,
            "sort_by": data.sort_by,
        },
    )


# ==========================================================
# HISTORIQUE DES RECHERCHES
# ==========================================================

@router.get("/history")
def get_search_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = (
        db.query(SearchHistory)
        .filter(
            SearchHistory.user_id == current_user.id
        )
        .order_by(SearchHistory.id.desc())
        .all()
    )

    return history