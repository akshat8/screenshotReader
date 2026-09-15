import logging

from app.graphs.processing_graph import get_processing_graph
from app.services.screenshot_service import update_screenshot_failed

logger = logging.getLogger(__name__)


async def process_screenshot(screenshot_id: str) -> None:
    """Run OCR, vision, embedding, and Pinecone upsert via LangGraph."""
    logger.info("Starting LangGraph processing for screenshot %s", screenshot_id)

    try:
        graph = get_processing_graph()
        await graph.ainvoke({"screenshot_id": screenshot_id, "halt": False})
    except Exception as exc:
        logger.exception("Processing failed for screenshot %s", screenshot_id)
        try:
            await update_screenshot_failed(screenshot_id, str(exc))
        except Exception as update_error:
            logger.exception(
                "Failed to update error status for screenshot %s: %s",
                screenshot_id,
                update_error,
            )
