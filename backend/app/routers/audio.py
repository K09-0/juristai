from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
import structlog
import os
import uuid
import magic

from app.config import ALLOWED_AUDIO_TYPES, MAX_FILE_SIZE
from app.database import get_supabase_client, check_rate_limit, increment_request_count
from app.routers.auth import get_user_id_from_request
from app.models.schemas import AudioProcessResponse, FileUploadResponse
from app.services.groq_service import get_groq_service
from app.config import is_admin

router = APIRouter()
logger = structlog.get_logger()
UPLOAD_DIR = "/tmp/juristai_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def validate_audio_file(content: bytes):
    if len(content) > MAX_FILE_SIZE:
        return False, "Файл слишком большой (>10MB)"
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(content)
    if file_type not in ALLOWED_AUDIO_TYPES:
        return False, "Формат не поддерживается"
    return True, ""

@router.post("/upload", response_model=FileUploadResponse)
async def upload_audio(file: UploadFile = File(...), username: Optional[str] = None, password: Optional[str] = None, user_id: str = Depends(get_user_id_from_request)):
    try:
        supabase = get_supabase_client()
        
        # Проверка админа
        if username and password:
            if not is_admin(username, password):
                limits = await check_rate_limit(supabase, user_id)
                if limits["remaining"] < 2:
                    raise HTTPException(status_code=429, detail="Нужно 2 запроса для аудио")
        else:
            limits = await check_rate_limit(supabase, user_id)
            if limits["remaining"] < 2:
                raise HTTPException(status_code=429, detail="Нужно 2 запроса для аудио")
        
        content = await file.read()
        is_valid, error = validate_audio_file(content)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        file_id = str(uuid.uuid4())
        ext = file.filename.split(".")[-1] if "." in file.filename else "mp3"
        path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
        
        with open(path, "wb") as f:
            f.write(content)
        
        return FileUploadResponse(file_id=file_id, filename=file.filename, file_type=f"audio/{ext}", file_size=len(content), status="uploaded", message="Файл загружен")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("audio_upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process/{file_id}", response_model=AudioProcessResponse)
async def process_audio(file_id: str, language: str = "ru", context: str = "consultation", username: Optional[str] = None, password: Optional[str] = None, background_tasks: BackgroundTasks = None, user_id: str = Depends(get_user_id_from_request)):
    try:
        supabase = get_supabase_client()
        
        # Проверка админа
        if username and password:
            if not is_admin(username, password):
                limits = await check_rate_limit(supabase, user_id)
                if limits["remaining"] < 2:
                    raise HTTPException(status_code=429, detail="Недостаточно запросов")
        else:
            limits = await check_rate_limit(supabase, user_id)
            if limits["remaining"] < 2:
                raise HTTPException(status_code=429, detail="Недостаточно запросов")
        
        files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(file_id)]
        if not files:
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        file_path = os.path.join(UPLOAD_DIR, files[0])
        
        groq = get_groq_service()
        transcription_result = await groq.transcribe_audio(audio_file_path=file_path, language=language, prompt=f"Юридическая {context}")
        text = transcription_result["text"]
        analysis = await groq.analyze_audio_content(text, context)
        
        if background_tasks:
            background_tasks.add_task(increment_request_count, supabase, user_id)
            background_tasks.add_task(increment_request_count, supabase, user_id)
            background_tasks.add_task(lambda: os.remove(file_path) if os.path.exists(file_path) else None)
        
        return AudioProcessResponse(transcription=text, summary=analysis.get("summary", ""), legal_entities=analysis.get("entities", []), recommended_queries=analysis.get("recommended_queries", []))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("audio_process_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
