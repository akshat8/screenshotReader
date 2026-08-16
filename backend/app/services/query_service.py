import logging
from typing import Any

from app.config import settings
from app.services.openrouter_service import generate_answer
from app.services.retrieval_service import get_context_documents, hybrid_search

logger = logging.getLogger(__name__)

NOT_FOUND_MESSAGE = (
    "I couldn't find enough information in your uploaded screenshots to answer this."
)


def is_relevant(hits: list) -> bool:
    if not hits:
        return False
    return hits[0].final_score >= settings.relevance_threshold


async def execute_query(user_query: str) -> dict[str, Any]:
    hits = await hybrid_search(user_query)
    if not is_relevant(hits):
        return {
            "answer": NOT_FOUND_MESSAGE,
            "sources": [],
            "found": False,
        }

    screenshot_ids = [hit.screenshot_id for hit in hits]
    context_documents = await get_context_documents(screenshot_ids)
    answer = await generate_answer(user_query, context_documents)

    sources = [
        {
            "id": hit.screenshot_id,
            "filename": hit.filename,
            "relevance": round(hit.final_score, 4),
        }
        for hit in hits
    ]

    return {
        "answer": answer,
        "sources": sources,
        "found": True,
    }
