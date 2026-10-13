from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages

from app.services.retrieval_service import RetrievalHit


class QueryState(TypedDict, total=False):
    user_query: str
    messages: Annotated[list, add_messages]
    goals: list[dict[str, str]]
    known_screenshot_ids: list[str]
    hits: list[RetrievalHit]
    context_documents: list[dict[str, Any]]
    agent_steps: int
    answer_rejections: int
    pending_stop: str
    tool_accepted: bool
    draft_answer: str
    revision_guidance: str
    critique_verdict: str
    revise_count: int
    search_again_count: int
    answer: str
    sources: list[dict[str, Any]]
    found: bool
    needs_clarification: bool
    decisions: list[dict[str, str]]


class ProcessingState(TypedDict, total=False):
    screenshot_id: str
    halt: bool
    document: dict[str, Any]
    image_path: str
    ocr_text: str
    image_description: str
    searchable_text: str
    embedding: list[float]
