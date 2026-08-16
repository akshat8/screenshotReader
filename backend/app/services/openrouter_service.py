import base64
import logging
from pathlib import Path

import httpx

from app.config import settings
from app.services.file_service import EXTENSION_TO_MEDIA_TYPE, get_extension

logger = logging.getLogger(__name__)

VISION_PROMPT = (
    "Describe this screenshot in 2-3 sentences. "
    "Focus on visible UI, conversations, numbers, and context."
)


def _encode_image_as_data_url(image_path: str) -> str:
    path = Path(image_path)
    extension = get_extension(path.name)
    media_type = EXTENSION_TO_MEDIA_TYPE.get(extension, "image/png")
    image_bytes = path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{media_type};base64,{encoded}"


async def _chat_completion(messages: list, model: str | None = None) -> str:
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    selected_model = model or settings.openrouter_vision_model
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": selected_model,
        "messages": messages,
    }
    url = f"{settings.openrouter_base_url.rstrip('/')}/chat/completions"

    last_error: Exception | None = None
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(
                    f"OpenRouter API error ({response.status_code}): {response.text[:200]}"
                )
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return str(content).strip()
        except Exception as exc:
            last_error = exc
            logger.warning("OpenRouter request attempt %s failed: %s", attempt + 1, exc)

    raise RuntimeError(f"OpenRouter request failed: {last_error}")


async def describe_image(image_path: str) -> str:
    data_url = _encode_image_as_data_url(image_path)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": VISION_PROMPT},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]
    description = await _chat_completion(messages)
    if not description:
        raise RuntimeError("OpenRouter returned an empty image description.")
    return description


def _format_context_block(document: dict) -> str:
    screenshot_id = str(document["_id"])
    filename = document.get("filename", "unknown")
    searchable_text = document.get("searchable_text") or ""
    if not searchable_text.strip():
        ocr_text = document.get("ocr_text") or ""
        image_description = document.get("image_description") or ""
        searchable_text = f"OCR:\n{ocr_text}\n\nIMAGE DESCRIPTION:\n{image_description}"

    return (
        f"Screenshot ID: {screenshot_id}\n"
        f"Filename: {filename}\n"
        f"Content:\n{searchable_text.strip()}"
    )


ANSWER_SYSTEM_PROMPT = (
    "You are a personal screenshot search assistant. "
    "Answer the user's question using ONLY the provided screenshot context.\n\n"
    "Rules:\n"
    "1. Do not use outside knowledge.\n"
    "2. Do not guess or invent information.\n"
    "3. If the answer cannot be found, say that the information was not found "
    "in the uploaded screenshots.\n"
    "4. Cite the screenshot IDs used for the answer.\n"
    "5. Keep the answer concise."
)


async def generate_answer(query: str, context_documents: list[dict]) -> str:
    if not context_documents:
        raise RuntimeError("No context documents provided for answer generation.")

    context_text = "\n\n---\n\n".join(
        _format_context_block(document) for document in context_documents
    )
    messages = [
        {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context_text}\n\nQuestion:\n{query}",
        },
    ]
    answer = await _chat_completion(messages, model=settings.openrouter_llm_model)
    if not answer:
        raise RuntimeError("OpenRouter returned an empty answer.")
    return answer
