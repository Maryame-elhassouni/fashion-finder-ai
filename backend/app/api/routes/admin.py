from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.ai_log import AILog
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Administration"])

class AIStatsResponse(BaseModel):
    total_calls:      int
    success_rate:     float
    avg_duration_ms:  float
    by_operation:     dict

@router.get("/ai-stats", response_model=AIStatsResponse)
def get_ai_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques d'utilisation de l'IA — utile pour le rapport PFE."""
    total = db.query(func.count(AILog.id)).scalar() or 0
    success_count = db.query(func.count(AILog.id)).filter(AILog.success == True).scalar() or 0
    avg_duration = db.query(func.avg(AILog.duration_ms)).scalar() or 0

    by_op_raw = (
        db.query(AILog.operation, func.count(AILog.id))
        .group_by(AILog.operation).all()
    )

    return AIStatsResponse(
       total_calls=total,
        success_rate=round((success_count / total * 100) if total > 0 else 100, 1),
        avg_duration_ms=round(avg_duration, 1),
        by_operation={op: count for op, count in by_op_raw}
    ) 