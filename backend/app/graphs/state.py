from typing import Any, TypedDict

from app.services.retrieval_service import RetrievalHit


class QueryState(TypedDict, total=False):
    user_query: str
    search_query: str
    next_search_query: str
    retrieval_attempts: int
    hits: list[RetrievalHit]
    context_documents: list[dict[str, Any]]
    decision_action: str
    clarifying_question: str
    answer: str
    sources: list[dict[str, Any]]
    found: bool
    needs_clarification: bool


class ProcessingState(TypedDict, total=False):
    screenshot_id: str
    halt: bool
    document: dict[str, Any]
    image_path: str
    ocr_text: str
    image_description: str
    searchable_text: str
    embedding: list[float]
