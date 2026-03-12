from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional
import structlog
import tempfile
import os

from app.services.groq_service import get_groq_service
from app.api.auth import require_auth

logger = structlog.get_logger()
router = APIRouter(prefix="/audio", tags=["audio"])

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = "ru",
    user_id: str = Depends(require_auth)
):
    """Транскрибация аудио (только Premium)."""
    try:
        # Сохраняем временно
        suffix = os.path.splitext(file.filename)[1] or ".mp3"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Транскрибируем
        groq = get_groq_service()
        result = await groq.transcribe_audio(tmp_path, language)
        
        # Удаляем временный файл
        os.unlink(tmp_path)
        
        # Анализируем содержимое
        analysis = await groq.analyze_audio_content(result["text"])
        
        logger.info("audio_transcribed", duration=result.get("duration"), user_id=user_id)
        
        return {
            "transcription": result["text"],
            "analysis": analysis,
            "duration": result.get("duration", 0),
            "language": result.get("language", language)
        }
        
    except Exception as e:
        logger.error("transcription_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Ошибка транскрибации: {str(e)}")
