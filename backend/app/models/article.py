from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base

class Article(Base):
    __tablename__ = "articles"
    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(200), nullable=False, index=True)
    description  = Column(Text, nullable=False)
    price        = Column(Float, nullable=False)
    brand        = Column(String(100))
    image_url    = Column(String(500))
    embedding_id = Column(String(100), unique=True)
    category_id  = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    category     = relationship("Category", back_populates="articles")
    __table_args__ = (
        Index("ix_articles_cat_price", "category_id", "price"),
    )