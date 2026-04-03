"""Configuration module for JurystAi backend"""
import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/juristai")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GOOGLE_GENAI_API_KEY: str = os.getenv("GOOGLE_GENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GOOGLE_GENAI_API_KEY", "")
    hf_api_token: str = os.getenv("HF_API_TOKEN", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://juristai.site,https://www.juristai.site,https://api.juristai.site").split(",")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    WORKERS: int = int(os.getenv("WORKERS", 4))
    premium_price_kzt: int = 5000
    kaspi_phone: str = "+77017891857"
    kaspi_cardholder: str = "JuristAI Premium"
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "change-me-in-production")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

def get_settings() -> Settings:
    """Get settings singleton"""
    return settings

def is_admin(username: str, password: str) -> bool:
    """Check if credentials are admin"""
    return username == settings.admin_username and password == settings.admin_password

ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg"]
MAX_FILE_SIZE = 10 * 1024 * 1024