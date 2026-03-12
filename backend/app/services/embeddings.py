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
