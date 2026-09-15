from app.config import settings


NOT_FOUND_MESSAGE = (
    "I couldn't find enough information in your uploaded screenshots to answer this."
)


def is_relevant(hits: list) -> bool:
    if not hits:
        return False
    return hits[0].final_score >= settings.relevance_threshold
