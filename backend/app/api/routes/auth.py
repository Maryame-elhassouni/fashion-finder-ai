from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.models.user import User
from backend.app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentification"])
@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.email, "id": user.id})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Connexion — retourne un token JWT."""
    user = db.query(User).filter(User.email == data.email).first()

    print("USER FOUND:", user)
    if user:
       print("DB HASH:", user.hashed_password)
       print("INPUT PASSWORD:", data.password)
       print("VERIFY RESULT:", verify_password(data.password, user.hashed_password))
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    token = create_access_token({"sub": user.email, "id": user.id})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )