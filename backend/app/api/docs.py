from fastapi import APIRouter

router = APIRouter()

@router.get("/all")
async def get_documentation():
    """Полная документация API"""
    return {
        "message": "Полная документация доступна на /docs (Swagger) или /redoc (ReDoc)",
        "endpoints": {
            "health": "/health - Проверка здоровья API",
            "auth_register": "POST /auth/register - Регистрация пользователя",
            "auth_login": "POST /auth/login - Вход пользователя",
            "auth_refresh": "POST /auth/refresh - Обновление токена",
            "docs": "/docs - Интерактивная документация (Swagger)",
            "redoc": "/redoc - Документация (ReDoc)"
        }
    }