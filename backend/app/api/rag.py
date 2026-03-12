from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import structlog
from datetime import datetime

from app.services.vector_store import get_vector_store
from app.services.groq_service import get_groq_service
from app.database import get_supabase_client
from app.api.auth import get_current_user_id, require_auth

logger = structlog.get_logger()
router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/query")
async def query_legal_documents(
    query: str,
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """
    Поиск ответа в нормативных документах РК.
    Бесплатно: 10 запросов/день, Premium: безлимит.
    """
    try:
        # Проверка лимитов для бесплатных пользователей
        if user_id:
            supabase = get_supabase_client()
            profile = supabase.table("users").select("is_premium, daily_requests_count, last_request_date").eq("id", user_id).single().execute()
            
            if profile.data:
                is_premium = profile.data.get("is_premium", False)
                daily_count = profile.data.get("daily_requests_count", 0)
                last_date = profile.data.get("last_request_date")
                today = datetime.now().date()
                
                # Сброс счетчика если новый день
                if last_date != str(today):
                    supabase.table("users").update({
                        "daily_requests_count": 1,
                        "last_request_date": today
                    }).eq("id", user_id).execute()
                elif not is_premium and daily_count >= 10:
                    raise HTTPException(
                        status_code=429,
                        detail="Дневной лимит исчерпан. Оформите Premium для безлимитного доступа."
                    )
                else:
                    # Увеличиваем счетчик
                    supabase.table("users").update({
                        "daily_requests_count": daily_count + 1
                    }).eq("id", user_id).execute()
        
        # Поиск по векторам
        vector_store = get_vector_store()
        contexts = await vector_store.search_similar(query, match_count=5, match_threshold=0.7)
        
        if not contexts:
            return {
                "answer": "Законодательство РК не содержит прямого ответа на данный вопрос в предоставленных документах.",
                "sources": [],
                "is_fallback": False,
                "warning": None
            }
        
        # Генерация ответа через LLM
        groq = get_groq_service()
        result = await groq.generate_rag_response(query, contexts)
        
        # Логирование запроса
        if user_id:
            supabase = get_supabase_client()
            supabase.table("query_logs").insert({
                "user_id": user_id,
                "query_text": query,
                "response_text": result["answer"][:500],
                "sources_used": result["sources_used"],
                "is_premium_request": not is_premium if 'is_premium' in locals() else False
            }).execute()
        
        logger.info("rag_query_success", query=query[:50], user_id=user_id, sources=len(contexts))
        
        return {
            "answer": result["answer"],
            "sources": [{"title": s, "relevance": 0.85} for s in result["sources_used"]],
            "is_fallback": result.get("is_fallback", False),
            "warning": result.get("warning"),
            "model_used": result.get("model_used", "unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("rag_query_failed", error=str(e), query=query[:50])
        raise HTTPException(status_code=500, detail=f"Ошибка обработки запроса: {str(e)}")

@router.get("/sources")
async def list_available_sources():
    """Список доступных нормативных документов."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("legal_documents").select("id, title, doc_type, doc_number, issue_date").execute()
        
        return {
            "sources": result.data if result.data else [],
            "count": len(result.data) if result.data else 0
        }
    except Exception as e:
        logger.error("list_sources_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Ошибка получения списка документов")

@router.post("/feedback")
async def submit_feedback(
    query_id: int,
    is_helpful: bool,
    comment: Optional[str] = None,
    user_id: str = Depends(require_auth)
):
    """Обратная связь по ответу (для улучшения качества)."""
    try:
        supabase = get_supabase_client()
        supabase.table("query_feedback").insert({
            "query_id": query_id,
            "user_id": user_id,
            "is_helpful": is_helpful,
            "comment": comment
        }).execute()
        
        return {"success": True, "message": "Спасибо за обратную связь!"}
    except Exception as e:
        logger.error("feedback_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Ошибка сохранения отзыва")
