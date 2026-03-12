import google.generativeai as genai
import structlog
from typing import Optional, Dict
from pathlib import Path

from app.config import get_settings

logger = structlog.get_logger()

class GeminiService:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def extract_text_from_image(self, image_path: str, prompt: Optional[str] = None) -> Dict:
        try:
            image_data = Path(image_path).read_bytes()
            default_prompt = """Извлеки весь текст из этого документа.\nСохрани структуру: заголовки, параграфы, списки.\nЕсли это таблица — представь в текстовом виде.\nУкажи тип документа (договор, иск, постановление и т.д.) если определишь."""
            response = self.model.generate_content([prompt or default_prompt, {"mime_type": "image/jpeg", "data": image_data}])
            return {"text": response.text, "document_type": self._detect_document_type(response.text), "confidence": "high" if len(response.text) > 100 else "medium", "model": "gemini-1.5-flash"}
        except Exception as e:
            logger.error("ocr_image_failed", error=str(e))
            raise
    
    async def extract_text_from_pdf_scan(self, pdf_path: str) -> Dict:
        try:
            import fitz
            doc = fitz.open(pdf_path)
            full_text = []
            for page_num in range(min(10, len(doc))):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                response = self.model.generate_content([f"Страница {page_num + 1} документа. Извлеки текст.", {"mime_type": "image/png", "data": img_data}])
                full_text.append(f"--- Страница {page_num + 1} ---\n{response.text}")
            doc.close()
            combined = "\n\n".join(full_text)
            return {"text": combined, "pages_processed": min(10, len(doc)), "document_type": self._detect_document_type(combined), "total_pages": len(doc)}
        except Exception as e:
            logger.error("ocr_pdf_failed", error=str(e))
            raise
    
    def _detect_document_type(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        indicators = {
            "договор": ["договор", "стороны", "предмет договора", "обязательства"],
            "иск": ["исковое заявление", "истец", "ответчик", "требования", "суд"],
            "жалоба": ["жалоба", "жалуется", "просит признать", "нарушение"],
            "претензия": ["претензия", "требуем", "возместить", "неустойка"],
            "протокол": ["протокол", "заседания", "присутствовали", "решили"],
            "постановление": ["постановление", "руководствуясь", "постоянной комиссии"]
        }
        scores = {}
        for doc_type, words in indicators.items():
            score = sum(1 for word in words if word in text_lower)
            if score > 0:
                scores[doc_type] = score
        if scores:
            return max(scores, key=scores.get)
        return "unknown"

_gemini_service = None

def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
