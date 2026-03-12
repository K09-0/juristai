from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import hashlib
import structlog

from app.database import get_supabase_client, check_rate_limit, get_or_create_user
from app.models.schemas import RateLimitResponse, PaymentRequest
from app.config import get_settings, is_admin

router = APIRouter()
logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)

def get_user_id_from_request(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), x_anon_id: Optional[str] = Header(None)) -> str:
    if credentials:
        return credentials.credentials
    if x_anon_id:
        return f"anon_{x_anon_id}"
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.md5(client_ip.encode()).hexdigest()[:16]
    return f"ip_{ip_hash}"

@router.get("/limits", response_model=RateLimitResponse)
async def get_rate_limits(
    request: Request,
    username: Optional[str] = None,
    password: Optional[str] = None,
    user_id: str = Depends(get_user_id_from_request)
):
    try:
        supabase = get_supabase_client()
        limits = await check_rate_limit(supabase, user_id, username, password)
        return limits
    except Exception as e:
        logger.error("get_limits_error", error=str(e))
        raise HTTPException(status_code=500, detail="Ошибка проверки лимитов")

@router.post("/login")
async def login(credentials: PaymentRequest, user_id: str = Depends(get_user_id_from_request)):
    if not credentials.username or not credentials.password:
        raise HTTPException(status_code=400, detail="Укажите username и password")
    
    if is_admin(credentials.username, credentials.password):
        return {
            "status": "admin_logged_in",
            "username": credentials.username,
            "access": "unlimited",
            "message": "Добро пожаловать, администратор!"
        }
    
    raise HTTPException(status_code=401, detail="Неверные credentials")

@router.post("/upgrade")
async def upgrade_to_premium(months: int = 1):
    settings = get_settings()
    amount = settings.premium_price_kzt * months
    
    return {
        "status": "pending_payment",
        "kaspi_phone": settings.kaspi_phone,
        "kaspi_cardholder": settings.kaspi_cardholder,
        "amount_kzt": amount,
        "instructions": f"Переведите {amount} тг на {settings.kaspi_phone} с комментарием 'JuristAI Premium {months}мес'"
    }
