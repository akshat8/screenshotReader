import logging
from typing import Any

from app.graphs.query_graph import get_query_graph

logger = logging.getLogger(__name__)

# Re-export for tests and API consumers.
from app.services.query_helpers import NOT_FOUND_MESSAGE, is_relevant  # noqa: F401


async def execute_query(user_query: str) -> dict[str, Any]:
    graph = get_query_graph()
    result = await graph.ainvoke({"user_query": user_query})

    return {
        "answer": result.get("answer", NOT_FOUND_MESSAGE),
        "sources": result.get("sources", []),
        "found": result.get("found", False),
        "needs_clarification": result.get("needs_clarification", False),
    }
