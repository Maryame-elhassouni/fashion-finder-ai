from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Category(Base):
    __tablename__ = "categories"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), unique=True, nullable=False)
    slug       = Column(String(100), unique=True, nullable=False)
    icon_emoji = Column(String(10), default="👗")
    articles   = relationship("Article", back_populates="category")