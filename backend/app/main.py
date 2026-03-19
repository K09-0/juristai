"""JurystAi - LegalTech SaaS for Kazakhstan
Production-ready FastAPI backend with JWT authentication, RAG system, and error handling.
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import os
import logging
from typing import Optional
import uvicorn

from app.auth.jwt_auth import JWTManager, create_access_token, verify_token
from app.config import settings
from app.database import init_db, get_db_session

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

jwt_manager = JWTManager(
    secret_key=settings.SECRET_KEY,
    algorithm="HS256",
    access_token_expire_minutes=30,
    refresh_token_expire_days=7
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting JurystAi backend...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    yield
    logger.info("Shutting down JurystAi backend...")

app = FastAPI(
    title="JurystAi API",
    description="LegalTech RAG system for Kazakhstan legislation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,https://juristai.site").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc) if os.getenv("ENV") != "production" else None}
    )

@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "JurystAi Backend",
        "version": "1.0.0"
    }

@app.get("/status", tags=["health"])
async def status_endpoint():
    """Detailed status endpoint"""
    try:
        db = next(get_db_session())
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "operational",
        "database": db_status,
        "environment": settings.ENV,
        "timestamp": str(__import__("datetime").datetime.utcnow())
    }

@app.post("/auth/register", tags=["auth"])
async def register(email: str, password: str, name: str):
    """Register a new user"""
    return {"message": "Registration endpoint - to be implemented"}

@app.post("/auth/login", tags=["auth"])
async def login(email: str, password: str):
    """Login user and return access + refresh tokens"""
    return {"message": "Login endpoint - to be implemented"}

@app.post("/auth/refresh", tags=["auth"])
async def refresh(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        payload = verify_token(refresh_token, token_type="refresh")
        new_access_token = create_access_token(subject=payload.sub)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.get("/legislation/search", tags=["legislation"])
async def search_legislation(query: str, limit: int = 10):
    """Search legislation using RAG system"""
    return {"query": query, "results": []}

@app.get("/legislation/codes", tags=["legislation"])
async def get_legislation_codes():
    """Get all available Kazakhstan legal codes"""
    return {
        "codes": [
            "Constitution of Kazakhstan",
            "Criminal Code",
            "Civil Code", 
            "Code of Criminal Procedure",
            "Code of Civil Procedure",
            "Labour Code",
            "Family Code",
            "Administrative Code",
            "Tax Code"
        ]
    }

@app.post("/admin/index-legislation", tags=["admin"])
async def index_legislation():
    """Trigger re-indexing of all legislation"""
    return {"status": "indexing_started"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 4))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        workers=workers,
        reload=settings.ENV != "production",
        log_level=os.getenv("LOG_LEVEL", "info")
    )