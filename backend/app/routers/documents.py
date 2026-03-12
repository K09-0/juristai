from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import structlog
import time

from app.database import get_supabase_client, check_rate_limit, increment_request_count, save_generated_document
from app.routers.auth import get_user_id_from_request
from app.models.schemas import DocumentGenerateRequest, DocumentGenerateResponse, ToneOfVoice, DocumentType
from app.services.groq_service import get_groq_service
from app.config import is_admin

router = APIRouter()
logger = structlog.get_logger()

@router.post("/generate", response_model=DocumentGenerateResponse)
async def generate_document(request: DocumentGenerateRequest, background_tasks: BackgroundTasks, user_id: str = Depends(get_user_id_from_request)):
    start_time = time.time()
    
    try:
        supabase = get_supabase_client()
        
        # Проверка админа
        if request.username and request.password:
            if not is_admin(request.username, request.password):
                limits = await check_rate_limit(supabase, user_id)
                if not limits["allowed"]:
                    raise HTTPException(status_code=429, detail=f"Лимит запросов исчерпан")
        else:
            limits = await check_rate_limit(supabase, user_id)
            if not limits["allowed"]:
                raise HTTPException(status_code=429, detail=f"Лимит запросов исчерпан. Осталось: {limits['remaining']}")
        
        groq = get_groq_service()
        generated_content = await groq.generate_document(doc_type=request.doc_type.value, tone=request.tone.value, facts=request.facts, parties=request.parties, demands=request.demands)
        
        doc_data = await save_generated_document(supabase=supabase, user_id=user_id, doc_type=request.doc_type.value, tone=request.tone.value, input_data={"facts": request.facts, "parties": request.parties, "demands": request.demands}, content=generated_content)
        
        background_tasks.add_task(increment_request_count, supabase, user_id)
        
        return DocumentGenerateResponse(id=doc_data["id"], doc_type=request.doc_type.value, tone=request.tone.value, content=generated_content, download_url=None, created_at=doc_data["created_at"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("document_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")

@router.get("/templates")
async def get_document_templates():
    templates = [
        {"type": DocumentType.CLAIM, "name": "Исковое заявление", "description": "Для подачи в суд при нарушении прав", "required_fields": ["истец", "ответчик", "предмет спора", "требования"]},
        {"type": DocumentType.CONTRACT, "name": "Договор", "description": "Договор подряда, купли-продажи, оказания услуг", "required_fields": ["заказчик", "исполнитель", "предмет договора", "сумма"]},
        {"type": DocumentType.COMPLAINT, "name": "Жалоба", "description": "В вышестоящие инстанции или надзорные органы", "required_fields": ["заявитель", "адресат", "суть жалобы"]},
        {"type": DocumentType.NOTICE, "name": "Претензия", "description": "Досудебное урегулирование спора", "required_fields": ["кредитор", "должник", "основание требования", "сумма"]}
    ]
    return {"templates": templates}
