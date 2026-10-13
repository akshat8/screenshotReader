import json
from dataclasses import asdict, dataclass
from typing import Any

from langchain_core.tools import tool

from app.config import settings
from app.services.retrieval_service import (
    RetrievalHit,
    get_context_documents,
    keyword_search,
    vector_search,
)

SNIPPET_CHAR_LIMIT = 500


@dataclass
class ToolObservation:
    text: str
    hits: list[RetrievalHit]
    documents: list[dict[str, Any]]


def _snippet_from_document(document: dict[str, Any]) -> str:
    text = (document.get("searchable_text") or "").strip()
    if not text:
        ocr_text = document.get("ocr_text") or ""
        image_description = document.get("image_description") or ""
        text = f"{ocr_text}\n{image_description}".strip()
    if not text:
        return "(empty)"
    if len(text) > SNIPPET_CHAR_LIMIT:
        return text[:SNIPPET_CHAR_LIMIT] + "…"
    return text


def _hits_from_score_map(
    scores: dict[str, float],
    *,
    score_kind: str,
    filename_map: dict[str, str],
    top_k: int,
) -> list[RetrievalHit]:
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
    hits: list[RetrievalHit] = []
    for screenshot_id, score in ordered:
        filename = filename_map.get(screenshot_id)
        if filename is None:
            continue
        semantic = score if score_kind == "semantic" else 0.0
        keyword = score if score_kind == "keyword" else 0.0
        hits.append(
            RetrievalHit(
                screenshot_id=screenshot_id,
                filename=filename,
                semantic_score=semantic,
                keyword_score=keyword,
                final_score=score,
            )
        )
    return hits


async def _filename_map(screenshot_ids: list[str]) -> dict[str, str]:
    documents = await get_context_documents(screenshot_ids)
    return {
        str(document["_id"]): document.get("filename", "unknown")
        for document in documents
    }


async def run_semantic_search(query: str) -> ToolObservation:
    top_k = settings.top_k
    pool_size = max(top_k * 2, 10)
    raw_scores = await vector_search(query, top_k=pool_size)
    max_score = max(raw_scores.values()) if raw_scores else 0.0
    normalized = {
        key: (value / max_score if max_score > 0 else 0.0)
        for key, value in raw_scores.items()
    }
    filename_map = await _filename_map(list(normalized))
    hits = _hits_from_score_map(
        normalized,
        score_kind="semantic",
        filename_map=filename_map,
        top_k=top_k,
    )
    if not hits:
        return ToolObservation(
            text=f"semantic_search({query!r}) returned no screenshots.",
            hits=[],
            documents=[],
        )

    lines = [
        f"semantic_search({query!r}) returned {len(hits)} screenshot(s):"
    ]
    for index, hit in enumerate(hits, start=1):
        lines.append(
            f"{index}. id={hit.screenshot_id} filename={hit.filename} "
            f"score={hit.final_score:.3f}"
        )
    return ToolObservation(text="\n".join(lines), hits=hits, documents=[])


async def run_keyword_search(query: str) -> ToolObservation:
    top_k = settings.top_k
    pool_size = max(top_k * 2, 10)
    try:
        scores = await keyword_search(query, top_k=pool_size)
    except Exception:
        scores = {}
    filename_map = await _filename_map(list(scores))
    hits = _hits_from_score_map(
        scores,
        score_kind="keyword",
        filename_map=filename_map,
        top_k=top_k,
    )
    if not hits:
        return ToolObservation(
            text=f"keyword_search({query!r}) returned no screenshots.",
            hits=[],
            documents=[],
        )

    lines = [
        f"keyword_search({query!r}) returned {len(hits)} screenshot(s):"
    ]
    for index, hit in enumerate(hits, start=1):
        lines.append(
            f"{index}. id={hit.screenshot_id} filename={hit.filename} "
            f"score={hit.final_score:.3f}"
        )
    return ToolObservation(text="\n".join(lines), hits=hits, documents=[])


async def run_read_screenshot(screenshot_id: str) -> ToolObservation:
    documents = await get_context_documents([screenshot_id])
    if not documents:
        return ToolObservation(
            text=f"read_screenshot({screenshot_id}) found no completed screenshot.",
            hits=[],
            documents=[],
        )

    document = documents[0]
    filename = document.get("filename", "unknown")
    snippet = _snippet_from_document(document)
    hit = RetrievalHit(
        screenshot_id=str(document["_id"]),
        filename=filename,
        semantic_score=0.0,
        keyword_score=0.0,
        final_score=1.0,
    )
    text = (
        f"read_screenshot({screenshot_id}) loaded filename={filename}\n"
        f"Content:\n{snippet}"
    )
    return ToolObservation(text=text, hits=[hit], documents=documents)


def observation_to_json(observation: ToolObservation) -> str:
    documents = []
    for document in observation.documents:
        payload = dict(document)
        if "_id" in payload:
            payload["_id"] = str(payload["_id"])
        documents.append(payload)
    return json.dumps(
        {
            "text": observation.text,
            "hits": [asdict(hit) for hit in observation.hits],
            "documents": documents,
        },
        default=str,
    )


def observation_from_json(raw: str) -> ToolObservation:
    payload = json.loads(raw)
    hits = [RetrievalHit(**hit) for hit in payload.get("hits") or []]
    return ToolObservation(
        text=str(payload.get("text") or ""),
        hits=hits,
        documents=list(payload.get("documents") or []),
    )


@tool
async def semantic_search(query: str) -> str:
    """Search uploaded screenshots by meaning using the vector index."""
    observation = await run_semantic_search(query)
    return observation_to_json(observation)


@tool
async def keyword_search(query: str) -> str:
    """Search uploaded screenshot text for exact words, names, or numbers."""
    observation = await run_keyword_search(query)
    return observation_to_json(observation)


@tool
async def read_screenshot(screenshot_id: str) -> str:
    """Load the full OCR text and description for one screenshot id."""
    observation = await run_read_screenshot(screenshot_id)
    return observation_to_json(observation)


@tool
def answer(reason: str) -> str:
    """Draft the user-facing answer from screenshots already loaded.

    Call this only when every goal is satisfied or blocked.
    """
    return reason


@tool
def clarify(question: str) -> str:
    """Ask one clarifying question when the user request is ambiguous."""
    return question


@tool
def give_up(reason: str) -> str:
    """Stop because the uploaded screenshots cannot answer the question."""
    return reason


RETRIEVAL_TOOLS = [semantic_search, keyword_search, read_screenshot]
STOP_TOOLS = [answer, clarify, give_up]
AGENT_TOOLS = RETRIEVAL_TOOLS + STOP_TOOLS
RETRIEVAL_TOOL_NAMES = {tool.name for tool in RETRIEVAL_TOOLS}
