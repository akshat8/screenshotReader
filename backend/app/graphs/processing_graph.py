import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Literal, TypeVar

from langgraph.graph import END, START, StateGraph

from app.graphs.state import ProcessingState
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

_processing_graph = None
_STAGE_ATTEMPTS = 2
_T = TypeVar("_T")


async def _run_with_retry(
    stage: str,
    screenshot_id: str,
    operation: Callable[[], Awaitable[_T]],
) -> _T:
    """Run a processing stage, retrying once on failure."""
    last_error: Exception | None = None
    for attempt in range(1, _STAGE_ATTEMPTS + 1):
        try:
            return await operation()
        except Exception as exc:
            last_error = exc
            logger.warning(
                "%s attempt %s/%s failed for screenshot %s: %s",
                stage,
                attempt,
                _STAGE_ATTEMPTS,
                screenshot_id,
                exc,
            )
    if last_error is None:
        raise RuntimeError(f"{stage} failed for screenshot {screenshot_id}.")
    raise last_error


async def load_document_node(state: ProcessingState) -> dict:
    screenshot_id = state["screenshot_id"]
    document = await get_screenshot_by_id(screenshot_id)
    if document is None:
        logger.error("Screenshot %s not found for processing", screenshot_id)
        return {"halt": True}

    absolute_path = resolve_file_path(document["file_path"])
    if not absolute_path.is_file():
        await update_screenshot_failed(
            screenshot_id,
            "Image file not found on disk.",
        )
        return {"halt": True}

    return {
        "document": document,
        "image_path": str(absolute_path),
        "halt": False,
    }


def route_after_load(
    state: ProcessingState,
) -> Literal["ocr", "__end__"]:
    if state.get("halt"):
        return END
    return "ocr"


async def ocr_node(state: ProcessingState) -> dict:
    screenshot_id = state["screenshot_id"]
    try:
        ocr_text = await _run_with_retry(
            "OCR",
            screenshot_id,
            lambda: asyncio.to_thread(extract_text, state["image_path"]),
        )
    except Exception as exc:
        await update_screenshot_failed(
            screenshot_id,
            f"OCR extraction failed: {exc}",
        )
        return {"halt": True}

    logger.info("LangGraph OCR completed for %s", screenshot_id)
    return {"ocr_text": ocr_text, "halt": False}


def route_after_ocr(
    state: ProcessingState,
) -> Literal["vision", "__end__"]:
    if state.get("halt"):
        return END
    return "vision"


async def vision_node(state: ProcessingState) -> dict:
    screenshot_id = state["screenshot_id"]
    try:
        image_description = await _run_with_retry(
            "Vision",
            screenshot_id,
            lambda: describe_image(state["image_path"]),
        )
    except Exception as exc:
        ocr_text = (state.get("ocr_text") or "").strip()
        if ocr_text:
            logger.warning(
                "Vision captioning failed for %s; continuing with OCR-only search: %s",
                screenshot_id,
                exc,
            )
            return {"image_description": "", "halt": False}

        await update_screenshot_failed(
            screenshot_id,
            f"Vision captioning failed and no OCR text was available: {exc}",
        )
        return {"halt": True, "image_description": ""}

    logger.info("LangGraph vision completed for %s", screenshot_id)
    return {"image_description": image_description, "halt": False}


def route_after_vision(
    state: ProcessingState,
) -> Literal["prepare_index", "__end__"]:
    if state.get("halt"):
        return END
    return "prepare_index"


async def prepare_index_node(state: ProcessingState) -> dict:
    searchable_text = build_searchable_text(
        state["ocr_text"],
        state["image_description"],
    )
    embedding = await asyncio.to_thread(embed_text, searchable_text)
    return {
        "searchable_text": searchable_text,
        "embedding": embedding,
    }


async def persist_node(state: ProcessingState) -> dict:
    screenshot_id = state["screenshot_id"]
    document = state["document"]

    await upsert_screenshot_vector(
        screenshot_id=screenshot_id,
        vector=state["embedding"],
        filename=document["filename"],
        snippet=state["searchable_text"],
    )
    await update_screenshot_completed(
        screenshot_id=screenshot_id,
        ocr_text=state["ocr_text"],
        image_description=state["image_description"],
        searchable_text=state["searchable_text"],
    )
    logger.info("LangGraph persist completed for %s", screenshot_id)
    return {}


def build_processing_graph():
    graph = StateGraph(ProcessingState)

    graph.add_node("load_document", load_document_node)
    graph.add_node("ocr", ocr_node)
    graph.add_node("vision", vision_node)
    graph.add_node("prepare_index", prepare_index_node)
    graph.add_node("persist", persist_node)

    graph.add_edge(START, "load_document")
    graph.add_conditional_edges("load_document", route_after_load)
    graph.add_conditional_edges("ocr", route_after_ocr)
    graph.add_conditional_edges("vision", route_after_vision)
    graph.add_edge("prepare_index", "persist")
    graph.add_edge("persist", END)

    return graph.compile()


def get_processing_graph():
    global _processing_graph
    if _processing_graph is None:
        _processing_graph = build_processing_graph()
    return _processing_graph
