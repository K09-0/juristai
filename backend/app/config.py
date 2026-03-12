from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # Supabase
    supabase_url: str = "https://your-project.supabase.co"
    supabase_key: str = "your-anon-key"
    
    # API Keys (заполнять через env vars!)
    groq_api_key: str = ""
    gemini_api_key: str = ""
    hf_api_token: str = ""
    
    # Security
    secret_key: str = "change-me-in-production-min-32-chars!!!"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Monetization
    kaspi_phone: str = "+77017891857"
    kaspi_cardholder: str = "Администратор JuristAI"
    premium_price_kzt: int = 5000
    
    # Admin credentials
    admin_username_1: str = "admin1"
    admin_password_1: str = "change-me-1"
    admin_username_2: str = "admin2"
    admin_password_2: str = "change-me-2"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Получить настройки (кэшируется)."""
    return Settings()
