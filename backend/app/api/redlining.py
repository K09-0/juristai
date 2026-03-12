from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Literal
import structlog
import tempfile
import os

from app.services.redlining_service import get_redlining_service
from app.api.auth import require_auth

logger = structlog.get_logger()
router = APIRouter(prefix="/redlining", tags=["redlining"])

@router.post("/analyze")
async def analyze_contract(
    file: UploadFile = File(...),
    party_role: str = "заказчик",
    risk_level: Literal["low", "medium", "high"] = "medium",
    user_id: str = Depends(require_auth)
):
    """Анализ договора с разметкой рисков (только Premium)."""
    try:
        # Проверяем формат
        if not file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="Только DOCX файлы")
        
        # Сохраняем
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            content = await file.read()
            tmp.write(content)
            input_path = tmp.name
        
        # Анализируем
        redlining = get_redlining_service()
        analysis = await redlining.analyze_contract(input_path, party_role, risk_level)
        
        # Создаем размеченный документ
        output_path = input_path.replace(".docx", "_analyzed.docx")
        redlining.create_redlined_document(input_path, output_path, analysis["risks"], party_role)
        
        # Читаем результат для отправки
        with open(output_path, "rb") as f:
            analyzed_content = f.read()
        
        # Удаляем временные файлы
        os.unlink(input_path)
        os.unlink(output_path)
        
        logger.info("contract_analyzed", risks_count=len(analysis["risks"]), user_id=user_id)
        
        return {
            "analysis": analysis,
            "risk_score": analysis["risk_score"],
            "risks_count": len(analysis["risks"]),
            "document_bytes": analyzed_content.hex()  # В реальности лучше через streaming
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("redlining_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")
