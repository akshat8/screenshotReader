"""Pure helpers for the query agent graph."""

import json
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.services.retrieval_service import RetrievalHit


def append_decision(
    state: dict,
    step: str,
    decision: str,
    reason: str,
) -> list[dict[str, str]]:
    decisions = list(state.get("decisions") or [])
    decisions.append(
        {
            "step": step,
            "decision": (decision or "")[:500],
            "reason": (reason or "")[:500],
        }
    )
    return decisions


def merge_hits(
    existing: list[RetrievalHit],
    new_hits: list[RetrievalHit],
) -> list[RetrievalHit]:
    by_id = {hit.screenshot_id: hit for hit in existing}
    for hit in new_hits:
        previous = by_id.get(hit.screenshot_id)
        if previous is None or hit.final_score >= previous.final_score:
            by_id[hit.screenshot_id] = hit
    merged = list(by_id.values())
    merged.sort(key=lambda item: item.final_score, reverse=True)
    return merged


def merge_documents(
    existing: list[dict],
    new_documents: list[dict],
) -> list[dict]:
    by_id = {str(document["_id"]): document for document in existing}
    for document in new_documents:
        by_id[str(document["_id"])] = document
    return list(by_id.values())


def build_sources(state: dict) -> list[dict]:
    hits = state.get("hits") or []
    context_documents = state.get("context_documents") or []
    document_map = {
        str(document["_id"]): document for document in context_documents
    }
    return [
        {
            "id": hit.screenshot_id,
            "filename": document_map[hit.screenshot_id]["filename"],
            "relevance": round(hit.final_score, 4),
        }
        for hit in hits
        if hit.screenshot_id in document_map
    ]


def last_ai_message(messages: list) -> AIMessage | None:
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            return message
    return None


def tool_messages_after_last_ai(messages: list) -> list[ToolMessage]:
    last_ai_index = None
    for index, message in enumerate(messages):
        if isinstance(message, AIMessage):
            last_ai_index = index
    if last_ai_index is None:
        return []
    return [
        message
        for message in messages[last_ai_index + 1 :]
        if isinstance(message, ToolMessage)
    ]


def acknowledge_open_tool_calls(messages: list, content: str) -> list[ToolMessage]:
    last_ai_index = None
    for index, message in enumerate(messages):
        if isinstance(message, AIMessage) and message.tool_calls:
            last_ai_index = index
    if last_ai_index is None:
        return []
    answered = {
        message.tool_call_id
        for message in messages[last_ai_index + 1 :]
        if isinstance(message, ToolMessage)
    }
    acknowledgements = []
    for call in messages[last_ai_index].tool_calls:
        if call["id"] in answered:
            continue
        acknowledgements.append(
            ToolMessage(
                content=content,
                tool_call_id=call["id"],
                name=call.get("name"),
            )
        )
    return acknowledgements


def call_args(call: dict) -> dict[str, Any]:
    args = call.get("args") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            return {}
    if not isinstance(args, dict):
        return {}
    return args


def tool_call_reason(call: dict) -> str:
    args = call_args(call)
    for key in ("reason", "query", "question", "screenshot_id"):
        value = args.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:500]
    return "Model selected this tool."


def tool_result_text(content: object) -> str:
    raw = content if isinstance(content, str) else str(content)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(payload, dict) and payload.get("text"):
        return str(payload["text"])
    return raw


def format_transcript(messages: list, limit: int = 4000) -> str:
    lines: list[str] = []
    for message in messages:
        if isinstance(message, HumanMessage):
            text = message.content if isinstance(message.content, str) else str(message.content)
            lines.append(f"User:\n{text}")
        elif isinstance(message, AIMessage) and message.tool_calls:
            call = message.tool_calls[0]
            lines.append(f"Tool call {call['name']}: {call_args(call)}")
        elif isinstance(message, ToolMessage):
            lines.append(f"Tool result:\n{tool_result_text(message.content)}")
    text = "\n\n".join(lines)
    if len(text) > limit:
        return text[:limit] + "…"
    return text or "No tool results yet."
