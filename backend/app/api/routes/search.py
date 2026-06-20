from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from pydantic import BaseModel, Field, field_validator
from backend.app.core.database import get_db
from backend.app.models.article import Article
from backend.app.models.category import Category
from backend.app.schemas.article import ArticleResponse

router = APIRouter(prefix="/search", tags=["Recherche"])


class SearchRequest(BaseModel):
    description: str = Field(..., min_length=1)
    category_filter: str | None = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La description ne peut pas être vide")
        return v

class SearchResponse(BaseModel):
    description:  str
    total:        int
    results:      list[ArticleResponse]
    search_type:  str = "keywords"

@router.post("/", response_model=SearchResponse)
def search_articles(data: SearchRequest, db: Session = Depends(get_db)):
    """Recherche par mots-clés (sera remplacée par Gemini en Semaine 3)."""
    keywords = [w.strip().lower() for w in data.description.split() if len(w) > 2]

    query = db.query(Article).options(joinedload(Article.category))

    if data.category_filter:
        query = query.join(Article.category).filter(
            Category.slug == data.category_filter
        )
    if keywords:
        conditions = [
            or_(
                Article.name.ilike(f"%{kw}%"),
                Article.description.ilike(f"%{kw}%")
            ) for kw in keywords[:5]
        ]
        query = query.filter(or_(*conditions))

    results = query.limit(8).all()
    return SearchResponse(
        description=data.description,
        total=len(results),
        results=results
    )    
