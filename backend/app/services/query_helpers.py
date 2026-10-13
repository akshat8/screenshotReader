from app.config import settings


NOT_FOUND_MESSAGE = (
    "I couldn't find enough information in your uploaded screenshots to answer this."
)


def get_max_agent_steps() -> int:
    configured = settings.max_agent_steps
    if configured < 1:
        return 1
    return min(configured, 6)
