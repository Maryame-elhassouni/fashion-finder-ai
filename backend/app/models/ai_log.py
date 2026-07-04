from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class AILog(Base):
    __tablename__ = "ai_logs"
    id              = Column(Integer, primary_key=True, index=True)
    operation       = Column(String(50))    # "vector_search", "classify", "enrich"
    success         = Column(Boolean, default=True)
    duration_ms     = Column(Integer)
    error_message   = Column(String(500), nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())