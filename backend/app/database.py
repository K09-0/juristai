from supabase import create_client, Client
from typing import Optional
import structlog

from app.config import get_settings

logger = structlog.get_logger()

class DatabaseError(Exception):
    """Кастомное исключение для ошибок БД."""
    pass

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Получить или создать клиент Supabase."""
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        logger.info("supabase_client_initialized")
    
    return _supabase_client

async def check_database_connection() -> bool:
    """Проверка подключения к БД."""
    try:
        client = get_supabase_client()
        # Простой запрос для проверки
        result = client.table("legal_documents").select("count", count="exact").limit(1).execute()
        logger.info("database_connection_ok", documents_count=result.count)
        return True
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))
        return False
