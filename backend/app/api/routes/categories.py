from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.category import Category
from app.schemas.article import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Catégories"])

@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Retourne les 6 catégories vestimentaires."""
    return db.query(Category).all()