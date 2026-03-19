"""Configuration module"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# AI/ML
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# RAG
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# CORS
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://www.juristai.site",
    "https://juristai.site",
    "*"
]