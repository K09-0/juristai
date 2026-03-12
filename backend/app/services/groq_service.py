import groq
import structlog
from typing import List, Dict, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

logger = structlog.get_logger()

class GroqService:
    MODEL_PRIMARY = "llama-3.1-70b-versatile"
    MODEL_FALLBACK = "llama-3.1-8b-instant"
    MODEL_WHISPER = "whisper-large-v3"
    
    def __init__(self):
        settings = get_settings()
        self.client = groq.Groq(api_key=settings.groq_api_key)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(1, 2, 10))
    async def generate_rag_response(self, query: str, contexts: List[Dict], temperature: float = 0.0, max_tokens: int = 2000) -> Dict:
        context_text = self._format_contexts(contexts)
        system_prompt = """Вы — юридический ассистент JuristAI, специализирующийся на законодательстве Республики Казахстан.

СТРОГИЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на основе предоставленного контекста из НПА РК.
2. Если ответа нет в контексте — честно скажи: "Законодательство РК не содержит прямого ответа на данный вопрос в предоставленных документах."
3. НЕ придумывай статьи, сроки, суммы, которые не указаны в контексте.
4. Цитируй конкретные статьи и пункты если они есть в контексте.
5. Указывай название документа (ГК РК, ТК РК и т.д.) при каждой цитате.
6. Температура 0 — ты детерминирован, не креативен.

Формат ответа:
- Прямой ответ на в
cat backend/app/services/groq_service.py | tail -20
rm -f backend/app/services/groq_service.py
wc -l backend/app/services/groq_service.pywc -l backend/app/services/groq_service.pywc -l backend/app/services/groq_service.pywc -l backend/app/services/groq_service.py
wc -l backend/app/services/groq_service.py
tail -3 backend/app/services/groq_service.py
@K09-0 ➜ /workspaces/juristai (main) $ 
cat > backend/app/services/embeddings.py << 'EOF'
import httpx
import structlog
import numpy as np
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import get_settings

logger = structlog.get_logger()
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

class EmbeddingsService:
    def __init__(self):
        settings = get_settings()
        self.token = settings.hf_api_token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.embedding_dim = 384
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(1, 2, 10), reraise=True)
    async def create_embedding(self, text: str) -> List[float]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(HF_API_URL, headers=self.headers, json={"inputs": text})
            if response.status_code == 503:
                logger.warning("hf_model_loading")
                raise Exception("Model is loading")
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list):
                    return result[0]
                return result
            raise ValueError(f"Unexpected response format")
    
    async def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(HF_API_URL, headers=self.headers, json={"inputs": texts})
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) == len(texts):
                return result
            raise ValueError(f"Batch embedding failed")
    
    def normalize_vector(self, vector: List[float]) -> List[float]:
        arr = np.array(vector)
        norm = np.linalg.norm(arr)
        if norm == 0:
            return vector
        return (arr / norm).tolist()

_embeddings_service = None

def get_embeddings_service() -> EmbeddingsService:
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service

async def get_embedding(text: str) -> List[float]:
    service = get_embeddings_service()
    return await service.create_embedding(text)
