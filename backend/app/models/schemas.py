from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ToneOfVoice(str, Enum):
    STRICT = "strict"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    SARCASTIC = "sarcastic"

class DocumentType(str, Enum):
    CLAIM = "claim"
    CONTRACT = "contract"
    COMPLAINT = "complaint"
    PETITION = "petition"
    LEGAL_OPINION = "legal_opinion"
    NOTICE = "notice"

class RateLimitResponse(BaseModel):
    allowed: bool
    current_count: int
    limit: int
    remaining: int
    is_premium: bool
    is_admin: bool = False
    payment_info: Optional[Dict] = None

class PaymentRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    months: int = 1

class PaymentResponse(BaseModel):
    status: str
    kaspi_phone: str
    kaspi_cardholder: str
    amount_kzt: int
    qr_code_url: Optional[str] = None
    instructions: str
    premium_until: Optional[str] = None

class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=1000)
    username: Optional[str] = None
    password: Optional[str] = None
    
    @validator('query')
    def validate_query(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Запрос слишком короткий')
        return v.strip()

class SourceCitation(BaseModel):
    document_title: str
    document_type: str
    chunk_text: str
    similarity_score: float
    article_number: Optional[str] = None

class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    processing_time_ms: int
    used_fallback: bool = False
    warning: Optional[str] = None

class DocumentGenerateRequest(BaseModel):
    doc_type: DocumentType
    tone: ToneOfVoice = ToneOfVoice.FORMAL
    facts: str = Field(..., min_length=20, max_length=5000)
    parties: Dict[str, str]
    demands: Optional[str] = Field(None, max_length=1000)
    username: Optional[str] = None
    password: Optional[str] = None
    
    @validator('facts')
    def validate_facts(cls, v):
        if len(v.strip()) < 20:
            raise ValueError('Описание фактов слишком короткое')
        return v.strip()

class DocumentGenerateResponse(BaseModel):
    id: int
    doc_type: str
    tone: str
    content: str
    download_url: Optional[str] = None
    created_at: datetime

class AudioProcessResponse(BaseModel):
    transcription: str
    summary: str
    legal_entities: List[Dict[str, Any]]
    recommended_queries: List[str]

class RedlineRequest(BaseModel):
    party_role: str
    risk_level: str = "medium"
    username: Optional[str] = None
    password: Optional[str] = None

class RedlineComment(BaseModel):
    id: str
    text_range: str
    original_text: str
    suggestion: str
    risk_type: str
    legal_basis: Optional[str] = None

class RedlineResponse(BaseModel):
    comments: List[RedlineComment]
    risk_score: int
    summary: str

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    message: str
