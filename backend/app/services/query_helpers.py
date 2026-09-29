from app.config import settings


NOT_FOUND_MESSAGE = (
    "I couldn't find enough information in your uploaded screenshots to answer this."
)


def is_relevant(hits: list) -> bool:
    """Score helper kept for callers that still want a numeric cutoff.

    Query routing does not use this. The planner node decides sufficiency.
    """
    if not hits:
        return False
    return hits[0].final_score >= settings.relevance_threshold


def get_max_retrieval_attempts() -> int:
    configured = settings.max_retrieval_attempts
    if configured < 1:
        return 1
    return min(configured, 3)
