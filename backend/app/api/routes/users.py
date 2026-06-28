from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_password, hash_password
from app.models.user import User
from app.models.search_history import SearchHistory
from app.schemas.auth import UserResponse, UserUpdate, UserStatsResponse

router = APIRouter(prefix="/users", tags=["Utilisateurs"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user
@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not data.full_name and not data.new_password:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")
    if data.full_name:
        current_user.full_name = data.full_name
    if data.new_password:
        if not verify_password(data.current_password or "", current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
        current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    db.refresh(current_user)
    return current_user
@router.get("/me/stats", response_model=UserStatsResponse)
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).count()
    last = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(SearchHistory.created_at.desc()).first()
    return UserStatsResponse(
        user=current_user,
        total_searches=total,
        last_search_at=last.created_at if last else None
    )