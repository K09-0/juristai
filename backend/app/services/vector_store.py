from typing import List, Dict, Optional
import structlog

from app.database import get_supabase_client, DatabaseError
from app.services.embeddings import get_embedding, get_embeddings_service

logger = structlog.get_logger()

class VectorStore:
    def __init__(self):
        self.embedding_dim = 384
    
    async def add_document(self, title: str, doc_type: str, content: str, doc_number: Optional[str] = None, issue_date: Optional[str] = None, source_url: Optional[str] = None, chunk_size: int = 500, chunk_overlap: int = 50) -> int:
        try:
            supabase = get_supabase_client()
            doc_data = {"title": title, "doc_type": doc_type, "doc_number": doc_number, "issue_date": issue_date, "content": content, "source_url": source_url}
            result = supabase.table("legal_documents").insert(doc_data).execute()
            document_id = result.data[0]["id"]
            
            chunks = self._split_into_chunks(content, chunk_size, chunk_overlap)
            logger.info("document_chunked", document_id=document_id, chunks_count=len(chunks))
            
            embedding_service = get_embeddings_service()
            embeddings = await embedding_service.create_embeddings_batch(chunks)
            
            chunk_records = []
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                norm_embedding = embedding_service.normalize_vector(embedding)
                chunk_records.append({"document_id": document_id, "chunk_text": chunk_text, "embedding": norm_embedding, "chunk_index": i, "metadata": {"char_start": i * (chunk_size - chunk_overlap), "char_end": i * (chunk_size - chunk_overlap) + len(chunk_text)}})
            
            supabase.table("document_chunks").insert(chunk_records).execute()
            logger.info("document_indexed", document_id=document_id, title=title, chunks=len(chunks))
            return document_id
            
        except Exception as e:
            logger.error("add_document_failed", error=str(e))
            raise DatabaseError(f"Не удалось добавить документ: {str(e)}")
    
    def _split_into_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + chunk_size, text_len)
            if end < text_len:
                search_start = max(end - 100, start)
                sentence_end = -1
                for i in range(end - 1, search_start - 1, -1):
                    if text[i] in '.!?':
                        sentence_end = i + 1
                        break
                if sentence_end > start:
                    end = sentence_end
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - overlap if end < text_len else text_len
        return chunks
    
    async def search_similar(self, query: str, match_count: int = 5, match_threshold: float = 0.7) -> List[Dict]:
        try:
            supabase = get_supabase_client()
            query_embedding = await get_embedding(query)
            result = supabase.rpc("match_documents", {"query_embedding": query_embedding, "match_threshold": match_threshold, "match_count": match_count}).execute()
            
            if not result.data:
                return []
            
            enriched_results = []
            for item in result.data:
                doc_result = supabase.table("legal_documents").select("title, doc_type, doc_number").eq("id", item["document_id"]).single().execute()
                doc_info = doc_result.data if doc_result.data else {}
                enriched_results.append({"chunk_id": item["id"], "document_id": item["document_id"], "document_title": doc_info.get("title", "Неизвестный документ"), "document_type": doc_info.get("doc_type", ""), "doc_number": doc_info.get("doc_number"), "chunk_text": item["chunk_text"], "similarity": item["similarity"], "chunk_index": item.get("chunk_index", 0)})
            
            logger.info("vector_search_completed", query=query[:50], results_count=len(enriched_results), top_score=enriched_results[0]["similarity"] if enriched_results else 0)
            return enriched_results
            
        except Exception as e:
            logger.error("vector_search_failed", error=str(e))
            raise DatabaseError(f"Ошибка векторного поиска: {str(e)}")

_vector_store = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
