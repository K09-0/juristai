"""Database connection management with Supabase"""
import os
from supabase import create_client, Client
import structlog
from typing import Optional
from datetime import datetime

logger = structlog.get_logger()

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create Supabase client singleton"""
    global _supabase_client

    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("supabase_client_initialized")

    return _supabase_client

async def check_rate_limit(supabase: Client, user_id: str, username: Optional[str] = None, password: Optional[str] = None) -> dict:
    """Check if user has exceeded rate limits"""
    from app.config import is_admin

    if username and password and is_admin(username, password):
        return {
            "allowed": True,
            "current_count": 0,
            "limit": -1,
            "remaining": -1,
            "is_premium": True,
            "is_admin": True
        }

    try:
        result = supabase.table("users").select("is_premium, daily_requests_count, last_request_date").eq("id", user_id).maybeSingle().execute()

        if not result.data:
            await get_or_create_user(supabase, user_id)
            return {
                "allowed": True,
                "current_count": 0,
                "limit": 10,
                "remaining": 10,
                "is_premium": False,
                "is_admin": False
            }

        user = result.data
        is_premium = user.get("is_premium", False)
        daily_count = user.get("daily_requests_count", 0)

        if is_premium:
            return {
                "allowed": True,
                "current_count": daily_count,
                "limit": -1,
                "remaining": -1,
                "is_premium": True,
                "is_admin": False
            }

        limit = 10
        remaining = max(0, limit - daily_count)

        return {
            "allowed": remaining > 0,
            "current_count": daily_count,
            "limit": limit,
            "remaining": remaining,
            "is_premium": False,
            "is_admin": False,
            "payment_info": {
                "kaspi_phone": "+77017891857",
                "price_kzt": 5000
            } if remaining == 0 else None
        }

    except Exception as e:
        logger.error("check_rate_limit_failed", error=str(e))
        return {
            "allowed": True,
            "current_count": 0,
            "limit": 10,
            "remaining": 10,
            "is_premium": False,
            "is_admin": False
        }

async def increment_request_count(supabase: Client, user_id: str):
    """Increment user's daily request count"""
    try:
        today = datetime.now().date()
        result = supabase.table("users").select("daily_requests_count, last_request_date").eq("id", user_id).maybeSingle().execute()

        if not result.data:
            await get_or_create_user(supabase, user_id)
            return

        user = result.data
        last_date = user.get("last_request_date")
        daily_count = user.get("daily_requests_count", 0)

        if last_date != str(today):
            supabase.table("users").update({
                "daily_requests_count": 1,
                "last_request_date": str(today)
            }).eq("id", user_id).execute()
        else:
            supabase.table("users").update({
                "daily_requests_count": daily_count + 1
            }).eq("id", user_id).execute()

    except Exception as e:
        logger.error("increment_request_count_failed", error=str(e))

async def get_or_create_user(supabase: Client, user_id: str) -> dict:
    """Get or create user profile"""
    try:
        result = supabase.table("users").select("*").eq("id", user_id).maybeSingle().execute()

        if result.data:
            return result.data

        new_user = {
            "id": user_id,
            "is_premium": False,
            "daily_requests_count": 0,
            "last_request_date": str(datetime.now().date()),
            "created_at": datetime.now().isoformat()
        }

        result = supabase.table("users").insert(new_user).execute()
        return result.data[0] if result.data else new_user

    except Exception as e:
        logger.error("get_or_create_user_failed", error=str(e))
        return {}

async def save_generated_document(supabase: Client, user_id: str, doc_type: str, tone: str, input_data: dict, content: str) -> dict:
    """Save generated document to database"""
    try:
        doc_data = {
            "user_id": user_id,
            "doc_type": doc_type,
            "tone": tone,
            "input_data": input_data,
            "content": content,
            "created_at": datetime.now().isoformat()
        }

        result = supabase.table("generated_documents").insert(doc_data).execute()
        return result.data[0] if result.data else doc_data

    except Exception as e:
        logger.error("save_document_failed", error=str(e))
        return {"id": 0, "created_at": datetime.now().isoformat()}

async def log_query(supabase: Client, user_id: str, session_id: Optional[str], query: str, response: str, sources: list, processing_time: int):
    """Log RAG query for analytics"""
    try:
        log_data = {
            "user_id": user_id,
            "session_id": session_id,
            "query_text": query,
            "response_text": response[:500],
            "sources_used": sources,
            "processing_time_ms": processing_time,
            "created_at": datetime.now().isoformat()
        }

        supabase.table("query_logs").insert(log_data).execute()

    except Exception as e:
        logger.error("log_query_failed", error=str(e))

async def activate_premium(supabase: Client, user_id: str, months: int) -> dict:
    """Activate premium subscription"""
    from datetime import timedelta

    try:
        premium_until = datetime.now() + timedelta(days=30 * months)

        result = supabase.table("users").update({
            "is_premium": True,
            "premium_until": premium_until.isoformat(),
            "daily_requests_count": 0
        }).eq("id", user_id).execute()

        return {
            "success": True,
            "premium_until": premium_until.isoformat(),
            "months": months
        }

    except Exception as e:
        logger.error("activate_premium_failed", error=str(e))
        raise

async def save_payment(supabase: Client, user_id: str, amount: int, months: int, status: str):
    """Save payment record"""
    try:
        payment_data = {
            "user_id": user_id,
            "amount_kzt": amount,
            "months": months,
            "status": status,
            "created_at": datetime.now().isoformat()
        }

        supabase.table("payments").insert(payment_data).execute()

    except Exception as e:
        logger.error("save_payment_failed", error=str(e))

class DatabaseError(Exception):
    """Custom database error"""
    pass