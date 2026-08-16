import asyncio
import logging

from app.services.embedding_service import embed_text
from app.services.file_service import resolve_file_path
from app.services.ocr_service import extract_text
from app.services.openrouter_service import describe_image
from app.services.pinecone_service import upsert_screenshot_vector
from app.services.screenshot_service import (
    get_screenshot_by_id,
    update_screenshot_completed,
    update_screenshot_failed,
)
from app.services.searchable_text import build_searchable_text

logger = logging.getLogger(__name__)


async def process_screenshot(screenshot_id: str) -> None:
    """Run OCR, vision, embedding, and Pinecone upsert for one screenshot."""
    logger.info("Starting processing for screenshot %s", screenshot_id)

    try:
        document = await get_screenshot_by_id(screenshot_id)
        if document is None:
            logger.error("Screenshot %s not found for processing", screenshot_id)
            return

        absolute_path = resolve_file_path(document["file_path"])
        if not absolute_path.is_file():
            await update_screenshot_failed(
                screenshot_id,
                "Image file not found on disk.",
            )
            return

        image_path = str(absolute_path)
        ocr_text = await asyncio.to_thread(extract_text, image_path)
        image_description = await describe_image(image_path)
        searchable_text = build_searchable_text(ocr_text, image_description)
        embedding = await asyncio.to_thread(embed_text, searchable_text)

        await upsert_screenshot_vector(
            screenshot_id=screenshot_id,
            vector=embedding,
            filename=document["filename"],
            snippet=searchable_text,
        )
        await update_screenshot_completed(
            screenshot_id=screenshot_id,
            ocr_text=ocr_text,
            image_description=image_description,
            searchable_text=searchable_text,
        )
        logger.info("Processing completed for screenshot %s", screenshot_id)
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
