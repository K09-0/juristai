from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Проверяем что DATABASE_URL установлен
if not settings.DATABASE_URL:
    logger.warning("DATABASE_URL not set, using SQLite for development")
    DATABASE_URL = "sqlite:///./test.db"
else:
    DATABASE_URL = settings.DATABASE_URL

# Параметры для PostgreSQL в продакшене
connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    connect_args = {}
else:
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        echo=settings.ENVIRONMENT == "development"
    )
    logger.info("✅ Database connection created")
except Exception as e:
    logger.error(f"❌ Failed to connect to database: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency для получения DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()