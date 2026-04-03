import groq
import structlog
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

class GroqService:
    MODEL_PRIMARY = "llama-3.1-70b-versatile"
    MODEL_FALLBACK = "llama-3.1-8b-instant"
    MODEL_WHISPER = "whisper-large-v3"

    def __init__(self, api_key: str):
        self.client = groq.Groq(api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_rag_response(self, query: str, contexts: List[Dict], temperature: float = 0.0, max_tokens: int = 2000) -> Dict:
        context_text = self._format_contexts(contexts)
        system_prompt = """Вы — юридический ассистент JuristAI, специализирующийся на законодательстве Республики Казахстан.

СТРОГИЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на основе предоставленного контекста из НПА РК.
2. Если ответа нет в контексте — честно скажи: "Законодательство РК не содержит прямого ответа на данный вопрос в предоставленных документах."
3. НЕ придумывай статьи, сроки, суммы, которые не указаны в контексте.
4. Цитируй конкретные статьи и пункты если они есть в контексте.
5. Указывай название документа (ГК РК, ТК РК и т.д.) при каждой цитате.

Формат ответа:
- Прямой ответ на вопрос
- Цитирование статей с названием документа
- Практические рекомендации"""

        user_message = f"""КОНТЕКСТ из законодательства РК:
{context_text}

ВОПРОС: {query}

Ответь строго на основе предоставленного контекста."""

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_PRIMARY,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            answer = response.choices[0].message.content
            sources_used = [ctx.get("document_title", "Неизвестный документ") for ctx in contexts[:3]]

            return {
                "answer": answer,
                "sources_used": sources_used,
                "model_used": self.MODEL_PRIMARY,
                "is_fallback": False
            }

        except Exception as e:
            logger.error("rag_generation_failed_primary", error=str(e))
            try:
                response = self.client.chat.completions.create(
                    model=self.MODEL_FALLBACK,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                answer = response.choices[0].message.content
                sources_used = [ctx.get("document_title", "Неизвестный документ") for ctx in contexts[:3]]

                return {
                    "answer": answer,
                    "sources_used": sources_used,
                    "model_used": self.MODEL_FALLBACK,
                    "is_fallback": True,
                    "warning": "Использована резервная модель"
                }
            except Exception as fallback_error:
                logger.error("rag_generation_failed_fallback", error=str(fallback_error))
                raise

    def _format_contexts(self, contexts: List[Dict]) -> str:
        formatted = []
        for i, ctx in enumerate(contexts, 1):
            title = ctx.get("document_title", "Документ")
            doc_type = ctx.get("document_type", "")
            chunk = ctx.get("chunk_text", "")
            doc_number = ctx.get("doc_number", "")

            header = f"[{i}] {title}"
            if doc_number:
                header += f" ({doc_number})"
            if doc_type:
                header += f" - {doc_type}"

            formatted.append(f"{header}\n{chunk}\n")

        return "\n".join(formatted)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_document(self, doc_type: str, tone: str, facts: str, parties: Dict[str, str], demands: Optional[str] = None) -> str:
        tone_instructions = {
            "strict": "максимально строгий и формальный",
            "formal": "официальный и вежливый",
            "friendly": "дружелюбный но профессиональный",
            "sarcastic": "с легкой иронией но в рамках приличия"
        }

        doc_templates = {
            "claim": "исковое заявление в суд",
            "contract": "договор между сторонами",
            "complaint": "жалобу в вышестоящую инстанцию",
            "notice": "претензию",
            "petition": "ходатайство",
            "legal_opinion": "юридическое заключение"
        }

        tone_text = tone_instructions.get(tone, "официальный")
        doc_name = doc_templates.get(doc_type, "юридический документ")

        parties_text = "\n".join([f"{role}: {name}" for role, name in parties.items()])

        prompt = f"""Составь {doc_name} на основе следующей информации.
Тон: {tone_text}

СТОРОНЫ:
{parties_text}

ФАКТИЧЕСКИЕ ОБСТОЯТЕЛЬСТВА:
{facts}"""

        if demands:
            prompt += f"\n\nТРЕБОВАНИЯ:\n{demands}"

        prompt += """\n\nТребования:
1. Структурированный документ с разделами
2. Ссылки на статьи законодательства РК где применимо
3. Юридически грамотный язык
4. Конкретные формулировки"""

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_PRIMARY,
                messages=[
                    {"role": "system", "content": "Вы - профессиональный юрист РК, составляете юридические документы."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error("document_generation_failed", error=str(e), doc_type=doc_type)
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def transcribe_audio(self, audio_file_path: str, language: str = "ru", prompt: Optional[str] = None) -> Dict:
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model=self.MODEL_WHISPER,
                    file=audio_file,
                    language=language,
                    prompt=prompt or "Юридическая консультация на русском языке"
                )

            return {
                "text": transcription.text,
                "language": language,
                "model": self.MODEL_WHISPER
            }

        except Exception as e:
            logger.error("audio_transcription_failed", error=str(e))
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def analyze_audio_content(self, transcription: str, context: str = "consultation") -> Dict:
        prompt = f"""Проанализируй следующую транскрипцию юридической {context}:

{transcription}

Предоставь:
1. Краткое резюме (2-3 предложения)
2. Выявленные юридические сущности (лица, организации, даты, суммы)
3. Рекомендуемые запросы для поиска в законодательстве РК (3-5 вопросов)"""

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_PRIMARY,
                messages=[
                    {"role": "system", "content": "Вы - юридический аналитик, специализирующийся на праве РК."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )

            content = response.choices[0].message.content

            return {
                "summary": content.split("1.")[1].split("2.")[0].strip() if "1." in content else content[:200],
                "entities": [],
                "recommended_queries": []
            }

        except Exception as e:
            logger.error("audio_analysis_failed", error=str(e))
            return {
                "summary": transcription[:200] + "...",
                "entities": [],
                "recommended_queries": []
            }

_groq_service = None

def get_groq_service() -> GroqService:
    global _groq_service
    if _groq_service is None:
        import os
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")
        _groq_service = GroqService(api_key)
    return _groq_service
