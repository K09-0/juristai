from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import time
import structlog

from app.database import get_supabase_client, check_rate_limit, increment_request_count, log_query
from app.routers.auth import get_user_id_from_request
from app.models.schemas import RAGQueryRequest, RAGQueryResponse, SourceCitation
from app.services.vector_store import get_vector_store
from app.services.groq_service import get_groq_service

router = APIRouter()
logger = structlog.get_logger()

@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest, background_tasks: BackgroundTasks, user_id: str = Depends(get_user_id_from_request)):
    start_time = time.time()
    
    try:
        supabase = get_supabase_client()
        
        # Проверка админа
        if request.username and request.password:
            from app.config import is_admin
            if not is_admin(request.username, request.password):
                limits = await check_rate_limit(supabase, user_id)
                if not limits["allowed"]:
                    raise HTTPException(status_code=429, detail=f"Дневной лимит исчерпан")
        else:
            limits = await check_rate_limit(supabase, user_id)
            if not limits["allowed"]:
                raise HTTPException(status_code=429, detail=f"Дневной лимит исчерпан ({limits['limit']} запросов/день)")
        
        vector_store = get_vector_store()
        contexts = await vector_store.search_similar(query=request.query, match_count=5, match_threshold=0.7)
        
        if not contexts:
            processing_time = int((time.time() - start_time) * 1000)
            background_tasks.add_task(increment_request_count, supabase, user_id)
            return RAGQueryResponse(
                answer="Законодательство РК не содержит прямого ответа на данный вопрос в доступных документах.",
                sources=[],
                processing_time_ms=processing_time,
                used_fallback=False,
                warning="Не найдены релевантные нормативные акты"
            )
        
        groq = get_groq_service()
        result = await groq.generate_rag_response(query=request.query, contexts=contexts, temperature=0.0, max_tokens=2000)
        
        sources = [SourceCitation(document_title=ctx["document_title"], document_type=ctx.get("document_type", ""), chunk_text=ctx["chunk_text"][:300] + "...", similarity_score=ctx["similarity"], article_number=ctx.get("doc_number")) for ctx in contexts[:3]]
        
        processing_time = int((time.time() - start_time) * 1000)
        
        background_tasks.add_task(increment_request_count, supabase, user_id)
        background_tasks.add_task(log_query, supabase, user_id, None, request.query, result["answer"], [{"title": s.document_title} for s in sources], processing_time)
        
        return RAGQueryResponse(answer=result["answer"], sources=sources, processing_time_ms=processing_time, used_fallback=result.get("is_fallback", False), warning=result.get("warning"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("rag_query_failed", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

@router.get("/history")
async def get_query_history(limit: int = 10, user_id: str = Depends(get_user_id_from_request)):
    try:
        supabase = get_supabase_client()
        result = supabase.table("query_logs").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return {"history": result.data or []}
    except Exception as e:
        logger.error("get_history_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Ошибка получения истории")
