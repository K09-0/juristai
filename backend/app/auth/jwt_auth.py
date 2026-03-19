"""JWT authentication and token management"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import logging
from fastapi import HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class TokenPayload(BaseModel):
    sub: str
    type: str
    exp: int

class JWTManager:
    """Manages JWT token creation and validation"""
    def __init__(self, secret_key: str, algorithm: str = "HS256", 
                 access_token_expire_minutes: int = 30,
                 refresh_token_expire_days: int = 7):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_access_token(self, subject: str, expires_delta: Optional[timedelta] = None) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {"sub": subject, "type": "access", "exp": int(expire.timestamp())}
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Access token created for subject: {subject}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise
    
    def create_refresh_token(self, subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        to_encode = {"sub": subject, "type": "refresh", "exp": int(expire.timestamp())}
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Refresh token created for subject: {subject}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise
    
    def verify_token(self, token: str, token_type: str = "access") -> TokenPayload:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                raise ValueError(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            logger.warning(f"Token expired")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

jwt_manager = None

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if not jwt_manager:
        raise RuntimeError("JWT manager not initialized")
    return jwt_manager.create_access_token(subject, expires_delta)

def create_refresh_token(subject: str) -> str:
    if not jwt_manager:
        raise RuntimeError("JWT manager not initialized")
    return jwt_manager.create_refresh_token(subject)

def verify_token(token: str, token_type: str = "access") -> TokenPayload:
    if not jwt_manager:
        raise RuntimeError("JWT manager not initialized")
    return jwt_manager.verify_token(token, token_type)