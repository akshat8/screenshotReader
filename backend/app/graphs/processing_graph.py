import asyncio
import logging
from typing import Literal

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
    ocr_text = await asyncio.to_thread(extract_text, state["image_path"])
    logger.info("LangGraph OCR completed for %s", state["screenshot_id"])
    return {"ocr_text": ocr_text}


async def vision_node(state: ProcessingState) -> dict:
    image_description = await describe_image(state["image_path"])
    logger.info("LangGraph vision completed for %s", state["screenshot_id"])
    return {"image_description": image_description}


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
    graph.add_edge("ocr", "vision")
    graph.add_edge("vision", "prepare_index")
    graph.add_edge("prepare_index", "persist")
    graph.add_edge("persist", END)

    return graph.compile()


def get_processing_graph():
    global _processing_graph
    if _processing_graph is None:
        _processing_graph = build_processing_graph()
    return _processing_graph
