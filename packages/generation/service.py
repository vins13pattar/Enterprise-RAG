try:
    from pydantic import BaseModel
except ModuleNotFoundError:  # pragma: no cover - used only in dependency-restricted checks
    class BaseModel:
        def __init__(self, **kwargs):
            for name in getattr(type(self), '__annotations__', {}):
                setattr(self, name, kwargs.get(name, getattr(type(self), name, None)))

        def model_dump(self):
            return dict(self.__dict__)

from packages.guardrails.service import inspect_text


class CitationOut(BaseModel):
    source_id: str
    document_name: str
    page: int | None = None
    chunk_id: str
    quote: str


class AnswerOut(BaseModel):
    answer: str
    citations: list[CitationOut]
    confidence: float
    grounded: bool
    needs_human_review: bool
    follow_up_questions: list[str] = []
    warnings: list[str] = []


class GenerationService:
    def generate(self, question: str, chunks: list, threshold=.55) -> AnswerOut:
        warnings = []
        if inspect_text(question)['pii']:
            warnings.append('PII detected in user input and redacted for logs')
        safe = [c for c in chunks if not inspect_text(c.text)['prompt_injection']]
        if not safe:
            return AnswerOut(answer='I do not know based on the available workspace documents.', citations=[], confidence=0, grounded=False, needs_human_review=True, warnings=warnings + ['No safe supporting context found'])
        top = safe[0]
        conf = max(0.1, min(0.95, top.score))
        quote = top.text[:180]
        return AnswerOut(answer=f'Based on the retrieved knowledge base, {quote}', citations=[CitationOut(source_id=top.source, document_name=top.source, page=top.page, chunk_id=top.chunk_id, quote=quote)], confidence=conf, grounded=True, needs_human_review=conf < threshold, warnings=warnings)
