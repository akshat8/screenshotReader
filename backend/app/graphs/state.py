from typing import Any, TypedDict

from app.services.retrieval_service import RetrievalHit


class QueryState(TypedDict, total=False):
    user_query: str
    hits: list[RetrievalHit]
    context_documents: list[dict[str, Any]]
    answer: str
    sources: list[dict[str, Any]]
    found: bool


class ProcessingState(TypedDict, total=False):
    screenshot_id: str
    halt: bool
    document: dict[str, Any]
    image_path: str
    ocr_text: str
    image_description: str
    searchable_text: str
    embedding: list[float]
