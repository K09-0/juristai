from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import sys

from app.config import get_settings
from app.database import check_database_connection
from app.api import auth, rag, documents, audio, redlining, payments

# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    logger.info("application_starting")
    
    # Проверка подключения к БД
    db_ok = await check_database_connection()
    if not db_ok:
        logger.error("database_not_available")
        # Не падаем, но предупреждаем
        print("⚠️ ВНИМАНИЕ: Нет подключения к Supabase!")
    
    logger.info("application_started", db_connected=db_ok)
    yield
    
    # Shutdown
    logger.info("application_stopping")

# Создание приложения
app = FastAPI(
    title="JuristAI API",
    description="Юридический AI-ассистент для Казахстана",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(rag.router)
app.include_router(documents.router)
app.include_router(audio.router)
app.include_router(redlining.router)
app.include_router(payments.router)

@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "name": "JuristAI API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "auth": "/auth",
            "rag": "/rag",
            "documents": "/documents",
            "audio": "/audio",
            "redlining": "/redlining",
            "payments": "/payments"
        }
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    db_ok = await check_database_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "timestamp": structlog.processors.TimeStamper()(None, None, {})
    }

@app.get("/admin/stats")
async def admin_stats():
    """Статистика для админ-панели (базовая)."""
    try:
        from app.database import get_supabase_client
        supabase = get_supabase_client()
        
        # Счетчики
        users_count = supabase.table("users").select("count", count="exact").execute().count or 0
        queries_count = supabase.table("query_logs").select("count", count="exact").execute().count or 0
        docs_count = supabase.table("legal_documents").select("count", count="exact").execute().count or 0
        
        return {
            "users_total": users_count,
            "queries_total": queries_count,
            "documents_indexed": docs_count,
            "premium_users": 0  # Можно добавить фильтр позже
        }
    except Exception as e:
        logger.error("admin_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
