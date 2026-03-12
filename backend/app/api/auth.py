from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from typing import Optional
import structlog

from app.database import get_supabase_client
from app.config import get_settings

logger = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

@router.post("/register")
async def register(email: str, password: str, full_name: Optional[str] = None):
    """Регистрация нового пользователя."""
    try:
        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name or email.split('@')[0]
                }
            }
        })
        
        if auth_response.user:
            logger.info("user_registered", user_id=auth_response.user.id, email=email)
            return {
                "success": True,
                "user_id": auth_response.user.id,
                "email": auth_response.user.email,
                "message": "Регистрация успешна. Проверьте email для подтверждения."
            }
        else:
            raise HTTPException(status_code=400, detail="Ошибка регистрации")
            
    except Exception as e:
        logger.error("registration_failed", error=str(e), email=email)
        raise HTTPException(status_code=400, detail=f"Ошибка регистрации: {str(e)}")

@router.post("/login")
async def login(email: str, password: str):
    """Вход пользователя."""
    try:
        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.session:
            logger.info("user_logged_in", user_id=auth_response.user.id)
            return {
                "success": True,
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "full_name": auth_response.user.user_metadata.get("full_name", "")
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Неверные учетные данные")
            
    except Exception as e:
        logger.error("login_failed", error=str(e), email=email)
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Обновление токена."""
    try:
        supabase = get_supabase_client()
        auth_response = supabase.auth.refresh_session(refresh_token)
        
        return {
            "success": True,
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token
        }
    except Exception as e:
        logger.error("token_refresh_failed", error=str(e))
        raise HTTPException(status_code=401, detail="Невалидный refresh token")

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получить текущего пользователя."""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(credentials.credentials)
        
        if user:
            profile = supabase.table("users").select("*").eq("id", user.user.id).single().execute()
            return {
                "id": user.user.id,
                "email": user.user.email,
                "full_name": user.user.user_metadata.get("full_name", ""),
                "is_premium": profile.data.get("is_premium", False) if profile.data else False,
                "daily_requests": profile.data.get("daily_requests_count", 0) if profile.data else 0
            }
        else:
            raise HTTPException(status_code=401, detail="Не авторизован")
    except Exception as e:
        logger.error("get_user_failed", error=str(e))
        raise HTTPException(status_code=401, detail="Не авторизован")

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """Dependency для получения ID пользователя."""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(credentials.credentials)
        return user.user.id if user else None
    except:
        return None

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Dependency для обязательной авторизации."""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Не авторизован")
        return user.user.id
    except Exception as e:
        logger.error("auth_required_failed", error=str(e))
        raise HTTPException(status_code=401, detail="Не авторизован")
