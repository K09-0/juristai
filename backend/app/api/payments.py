from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import structlog
from datetime import datetime, timedelta

from app.database import get_supabase_client
from app.config import get_settings
from app.api.auth import require_auth

logger = structlog.get_logger()
router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/status")
async def get_payment_status(user_id: str = Depends(require_auth)):
    """Статус подписки пользователя."""
    try:
        supabase = get_supabase_client()
        profile = supabase.table("users").select("is_premium, premium_until, daily_requests_count").eq("id", user_id).single().execute()
        
        if not profile.data:
            raise HTTPException(status_code=404, detail="Профиль не найден")
        
        data = profile.data
        is_premium = data.get("is_premium", False)
        premium_until = data.get("premium_until")
        
        # Проверяем не истекла ли подписка
        if is_premium and premium_until:
            expiry = datetime.fromisoformat(premium_until.replace("Z", "+00:00"))
            if expiry < datetime.now(expiry.tzinfo):
                is_premium = False
                supabase.table("users").update({"is_premium": False}).eq("id", user_id).execute()
        
        return {
            "is_premium": is_premium,
            "premium_until": premium_until,
            "daily_requests_used": data.get("daily_requests_count", 0),
            "daily_requests_limit": 10 if not is_premium else "unlimited",
            "price_kzt": 5000,
            "kaspi_phone": "+77017891857"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("payment_status_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Ошибка получения статуса")

@router.post("/create")
async def create_payment_request(
    months: int = 1,
    user_id: str = Depends(require_auth)
):
    """Создание запроса на оплату."""
    try:
        settings = get_settings()
        amount = settings.premium_price_kzt * months
        
        supabase = get_supabase_client()
        result = supabase.table("payments").insert({
            "user_id": user_id,
            "amount_kzt": amount,
            "months": months,
            "status": "pending"
        }).execute()
        
        payment_id = result.data[0]["id"] if result.data else None
        
        return {
            "payment_id": payment_id,
            "amount_kzt": amount,
            "months": months,
            "kaspi_phone": settings.kaspi_phone,
            "instructions": f"Переведите {amount} тг на Kaspi {settings.kaspi_phone} с комментарием 'JuristAI Premium {payment_id}'"
        }
        
    except Exception as e:
        logger.error("payment_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Ошибка создания платежа")
