import logging
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.config import settings
from app.graphs.state import QueryState
from app.services.openrouter_service import generate_answer
from app.services.query_helpers import NOT_FOUND_MESSAGE, is_relevant
from app.services.retrieval_service import get_context_documents, hybrid_search

logger = logging.getLogger(__name__)

_query_graph = None


async def retrieve_node(state: QueryState) -> dict:
    hits = await hybrid_search(state["user_query"])
    logger.info("LangGraph retrieve: %s hits for query", len(hits))
    return {"hits": hits}


def route_after_retrieve(
    state: QueryState,
) -> Literal["load_context", "not_found"]:
    hits = state.get("hits") or []
    if not is_relevant(hits):
        return "not_found"
    return "load_context"


async def load_context_node(state: QueryState) -> dict:
    hits = state.get("hits") or []
    screenshot_ids = [hit.screenshot_id for hit in hits]
    context_documents = await get_context_documents(screenshot_ids)
    logger.info(
        "LangGraph load_context: %s documents for %s hits",
        len(context_documents),
        len(hits),
    )
    return {"context_documents": context_documents}


def route_after_load_context(
    state: QueryState,
) -> Literal["generate", "not_found"]:
    if not state.get("context_documents"):
        return "not_found"
    return "generate"


async def generate_node(state: QueryState) -> dict:
    hits = state.get("hits") or []
    context_documents = state.get("context_documents") or []
    user_query = state["user_query"]

    answer = await generate_answer(user_query, context_documents)
    document_map = {str(document["_id"]): document for document in context_documents}

    sources = [
        {
            "id": hit.screenshot_id,
            "filename": document_map[hit.screenshot_id]["filename"],
            "relevance": round(hit.final_score, 4),
        }
        for hit in hits
        if hit.screenshot_id in document_map
    ]

    return {
        "answer": answer,
        "sources": sources,
        "found": True,
    }


async def not_found_node(_state: QueryState) -> dict:
    return {
        "answer": NOT_FOUND_MESSAGE,
        "sources": [],
        "found": False,
    }


def build_query_graph():
    graph = StateGraph(QueryState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("load_context", load_context_node)
    graph.add_node("generate", generate_node)
    graph.add_node("not_found", not_found_node)

    graph.add_edge(START, "retrieve")
    graph.add_conditional_edges("retrieve", route_after_retrieve)
    graph.add_conditional_edges("load_context", route_after_load_context)
    graph.add_edge("generate", END)
    graph.add_edge("not_found", END)

    return graph.compile()


def get_query_graph():
    global _query_graph
    if _query_graph is None:
        _query_graph = build_query_graph()
    return _query_graph
