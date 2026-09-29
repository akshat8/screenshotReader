import logging
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.graphs.state import QueryState
from app.services.openrouter_service import generate_answer
from app.services.query_helpers import NOT_FOUND_MESSAGE, get_max_retrieval_attempts
from app.services.query_planner import plan_retrieval
from app.services.retrieval_service import get_context_documents, hybrid_search

logger = logging.getLogger(__name__)

_query_graph = None


async def retrieve_node(state: QueryState) -> dict:
    candidate = (state.get("next_search_query") or "").strip()
    query = candidate or state.get("search_query") or state["user_query"]
    hits = await hybrid_search(query)
    attempt = state.get("retrieval_attempts", 0) + 1
    logger.info("LangGraph retrieve: %s hits on attempt %s", len(hits), attempt)
    return {
        "hits": hits,
        "search_query": query,
        "next_search_query": "",
        "retrieval_attempts": attempt,
    }


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


async def plan_node(state: QueryState) -> dict:
    max_attempts = get_max_retrieval_attempts()
    decision = await plan_retrieval(
        user_query=state["user_query"],
        search_query=state.get("search_query") or state["user_query"],
        hits=state.get("hits") or [],
        context_documents=state.get("context_documents") or [],
        retrieval_attempt=state.get("retrieval_attempts", 1),
        max_attempts=max_attempts,
    )
    return {
        "decision_action": decision.action,
        "next_search_query": decision.reformulated_query or "",
        "clarifying_question": decision.clarifying_question or "",
    }


def route_after_plan(
    state: QueryState,
) -> Literal["generate", "retrieve", "clarify", "not_found"]:
    action = state.get("decision_action")
    documents = state.get("context_documents") or []
    attempts = state.get("retrieval_attempts", 1)
    max_attempts = get_max_retrieval_attempts()

    if action == "sufficient" and documents:
        return "generate"

    if action == "reformulate" and attempts < max_attempts:
        candidate = (state.get("next_search_query") or "").strip()
        current = (state.get("search_query") or "").strip()
        if candidate and candidate.casefold() != current.casefold():
            return "retrieve"

    if action == "clarify" and (state.get("clarifying_question") or "").strip():
        return "clarify"

    return "not_found"


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
        "needs_clarification": False,
    }


async def clarify_node(state: QueryState) -> dict:
    question = (state.get("clarifying_question") or "").strip()
    return {
        "answer": question or NOT_FOUND_MESSAGE,
        "sources": [],
        "found": False,
        "needs_clarification": bool(question),
    }


async def not_found_node(_state: QueryState) -> dict:
    return {
        "answer": NOT_FOUND_MESSAGE,
        "sources": [],
        "found": False,
        "needs_clarification": False,
    }


def build_query_graph():
    graph = StateGraph(QueryState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("load_context", load_context_node)
    graph.add_node("plan", plan_node)
    graph.add_node("generate", generate_node)
    graph.add_node("clarify", clarify_node)
    graph.add_node("not_found", not_found_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "load_context")
    graph.add_edge("load_context", "plan")
    graph.add_conditional_edges("plan", route_after_plan)
    graph.add_edge("generate", END)
    graph.add_edge("clarify", END)
    graph.add_edge("not_found", END)

    return graph.compile()


def get_query_graph():
    global _query_graph
    if _query_graph is None:
        _query_graph = build_query_graph()
    return _query_graph
