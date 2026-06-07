from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base

class SearchHistory(Base):
    __tablename__ = "search_history"
    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    description     = Column(String(500), nullable=False)
    category_filter = Column(String(50))
    results_count   = Column(Integer, default=0)
    duration_ms     = Column(Integer)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    user            = relationship("User", back_populates="search_history")