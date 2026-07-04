from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

# =========================
# PASSWORD
# =========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Auth obligatoire
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

# Auth optionnelle (important pour /search)
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# =========================
# JWT
# =========================

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_token(token: str):
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        return None


# =========================
# CURRENT USER (obligatoire)
# =========================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    from app.models.user import User

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Token invalide ou expiré"
        )

    email = payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Token invalide"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Utilisateur introuvable"
        )

    return user


# =========================
# CURRENT USER (optionnel)
# =========================

def get_optional_user(
    token: str | None = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Retourne l'utilisateur connecté si un JWT valide est fourni.
    Retourne None si aucun token ou token invalide.
    """

    if token is None:
        return None

    payload = decode_token(token)

    if payload is None:
        return None

    email = payload.get("sub")

    if email is None:
        return None

    from app.models.user import User

    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None or not user.is_active:
        return None

    return user