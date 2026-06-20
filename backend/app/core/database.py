from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

engine = None
SessionLocal = None


def init_engine(db_url: str):
    global engine, SessionLocal

    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
    )

    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )

    return engine


def get_db():
    if SessionLocal is None:
        raise Exception("DB not initialized. Call init_engine() first.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()