from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.article import Article
from backend.app.models.category import Category
from backend.app.models.user import User
from backend.app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleResponse,
    ArticleListResponse, ArticleStats
)
router = APIRouter(prefix="/articles", tags=["Articles"])

@router.get("/", response_model=ArticleListResponse)
def get_articles(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=50),
    db:   Session = Depends(get_db)
):
    """Liste paginée de tous les articles."""
    offset = (page - 1) * size
    total  = db.query(Article).count()
    items  = (
        db.query(Article)
        .options(joinedload(Article.category))
        .offset(offset)
        .limit(size)
        .all()
    )
    return ArticleListResponse(total=total, page=page, size=size, articles=items)
@router.get("/stats", response_model=ArticleStats)
def get_articles_stats(db: Session = Depends(get_db)):
    """Statistiques globales du catalogue."""
    from sqlalchemy import func
    stats = db.query(
        func.count(Article.id).label("total"),
        func.avg(Article.price).label("avg_price"),
        func.min(Article.price).label("min_price"),
        func.max(Article.price).label("max_price"),
    ).first()

    by_cat_raw = (
        db.query(Category.slug, func.count(Article.id).label("count"))
        .join(Article, Article.category_id == Category.id)
        .group_by(Category.slug)
        .all()
    )
    by_category = {row.slug: row.count for row in by_cat_raw}
    total_cats  = db.query(func.count(Category.id)).scalar()

    return ArticleStats(
        total_articles   = stats.total or 0,
        total_categories = total_cats or 0,
        avg_price        = round(stats.avg_price or 0, 2),
        min_price        = stats.min_price or 0,
        max_price        = stats.max_price or 0,
        by_category      = by_category
    )
@router.get("/category/{slug}", response_model=ArticleListResponse)
def get_articles_by_category(
    slug: str,
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=50),
    db:   Session = Depends(get_db)
):
    """Articles filtrés par slug de catégorie."""
    query = (
        db.query(Article)
        .options(joinedload(Article.category))
        .join(Article.category)
        .filter(Category.slug == slug)
    )
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return ArticleListResponse(total=total, page=page, size=size, articles=items)

@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Détail d'un article par son ID."""
    article = (
        db.query(Article)
        .options(joinedload(Article.category))
        .filter(Article.id == article_id)
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return article
@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article(
    data:         ArticleCreate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user)
):
    """Créer un nouvel article vestimentaire (authentifié)."""
    cat = db.query(Category).filter(Category.id == data.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie introuvable")
    article = Article(**data.model_dump())
    db.add(article)
    db.commit()
    db.refresh(article)

    article = (
        db.query(Article)
        .options(joinedload(Article.category))
        .filter(Article.id == article.id)
        .first()
    )
    return article
@router.patch("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id:   int,
    data:         ArticleUpdate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user)
):
    """Mise à jour partielle (PATCH) — seuls les champs fournis sont modifiés."""
    article = (
        db.query(Article)
        .options(joinedload(Article.category))
        .filter(Article.id == article_id)
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")

    update_data = data.to_update_dict()
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucun champ fourni")

    if "category_id" in update_data:
        if not db.query(Category).filter(Category.id == update_data["category_id"]).first():
            raise HTTPException(status_code=404, detail="Catégorie introuvable")

    for field, value in update_data.items():
        setattr(article, field, value)
    db.commit()
    db.refresh(article)

    return (
        db.query(Article)
        .options(joinedload(Article.category))
        .filter(Article.id == article_id)
        .first()
    )    
@router.delete("/{article_id}", status_code=204)
def delete_article(
    article_id:   int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user)
):
    """Supprimer un article (authentifié)."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")
    db.delete(article)
    db.commit()
    return None