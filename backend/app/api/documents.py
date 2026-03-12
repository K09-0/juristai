from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional
import structlog

from app.services.groq_service import get_groq_service
from app.api.auth import get_current_user_id, require_auth

logger = structlog.get_logger()
router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/generate")
async def generate_document(
    doc_type: str,
    tone: str,
    facts: str,
    parties: Dict[str, str],
    demands: Optional[str] = None,
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """Генерация юридического документа (иск, претензия, договор)."""
    try:
        groq = get_groq_service()
        document = await groq.generate_document(doc_type, tone, facts, parties, demands)
        
        logger.info("document_generated", doc_type=doc_type, tone=tone, user_id=user_id)
        
        return {
            "document": document,
            "doc_type": doc_type,
            "tone": tone,
            "word_count": len(document.split())
        }
    except Exception as e:
        logger.error("document_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")
