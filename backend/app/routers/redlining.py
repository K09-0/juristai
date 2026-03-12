from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import structlog
import os
import magic

from app.config import MAX_FILE_SIZE
from app.database import get_supabase_client, check_rate_limit, increment_request_count
from app.routers.auth import get_user_id_from_request
from app.models.schemas import FileUploadResponse, RedlineRequest, RedlineResponse, RedlineComment
from app.services.redlining_service import get_redlining_service
from app.config import is_admin

router = APIRouter()
logger = structlog.get_logger()
UPLOAD_DIR = "/tmp/juristai_uploads"

@router.post("/upload", response_model=FileUploadResponse)
async def upload_contract(file: UploadFile = File(...), user_id: str = Depends(get_user_id_from_request)):
    try:
        supabase = get_supabase_client()
        limits = await check_rate_limit(supabase, user_id)
        if not limits["allowed"]:
            raise HTTPException(status_code=429, detail="Лимит исчерпан")
        
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Файл >10MB")
        
        mime = magic.Magic(mime=True)
        if "word" not in mime.from_buffer(content) and content[:4] != b'PK\x03\x04':
            raise HTTPException(status_code=400, detail="Требуется DOCX")
        
        file_id = f"contract_{user_id[:8]}_{os.urandom(4).hex()}"
        path = os.path.join(UPLOAD_DIR, f"{file_id}.docx")
        
        with open(path, "wb") as f:
            f.write(content)
        
        return FileUploadResponse(file_id=file_id, filename=file.filename, file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", file_size=len(content), status="ready", message="Договор загружен")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/{file_id}", response_model=RedlineResponse)
async def analyze_contract(file_id: str, params: RedlineRequest, background_tasks: BackgroundTasks, user_id: str = Depends(get_user_id_from_request)):
    try:
        supabase = get_supabase_client()
        
        # Проверка админа
        if params.username and params.password:
            if not is_admin(params.username, params.password):
                limits = await check_rate_limit(supabase, user_id)
                if limits["remaining"] < 3:
                    raise HTTPException(status_code=429, detail="Нужно 3 запроса для анализа")
        else:
            limits = await check_rate_limit(supabase, user_id)
            if limits["remaining"] < 3:
                raise HTTPException(status_code=429, detail="Нужно 3 запроса для анализа")
        
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}.docx")
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        service = get_redlining_service()
        analysis = await service.analyze_contract(docx_path=input_path, party_role=params.party_role, risk_level=params.risk_level)
        
        output_path = os.path.join(UPLOAD_DIR, f"{file_id}_redlined.docx")
        service.create_redlined_document(input_path=input_path, output_path=output_path, risks=analysis["risks"], party_role=params.party_role)
        
        for _ in range(3):
            background_tasks.add_task(increment_request_count, supabase, user_id)
        
        comments = [RedlineComment(**r) for r in analysis["risks"]]
        return RedlineResponse(comments=comments, risk_score=analysis["risk_score"], summary=analysis["summary"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("analysis_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_id}")
async def download_redlined(file_id: str):
    path = os.path.join(UPLOAD_DIR, f"{file_id}_redlined.docx")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path, filename=f"contract_redlined_{file_id[:8]}.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
