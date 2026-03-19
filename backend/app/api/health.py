from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Проверка здоровья API"""
    
    try:
        # Проверяем БД
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "error"
    
    return {
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "database": db_status,
        "service": "JurystAi API"
    }