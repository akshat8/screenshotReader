import asyncio
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

_index = None
_pinecone_client = None

METADATA_SNIPPET_MAX_LENGTH = 500


def _get_index():
    global _pinecone_client, _index
    if not settings.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY is not configured.")

    if _index is None:
        from pinecone import Pinecone

        logger.info("Connecting to Pinecone index: %s", settings.pinecone_index_name)
        _pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
        _index = _pinecone_client.Index(settings.pinecone_index_name)
    return _index


def _upsert_vector(
    screenshot_id: str,
    vector: list[float],
    filename: str,
    snippet: str,
) -> None:
    if len(vector) != settings.pinecone_dimension:
        raise RuntimeError(
            f"Embedding dimension {len(vector)} does not match "
            f"PINECONE_DIMENSION {settings.pinecone_dimension}."
        )

    index = _get_index()
    metadata: dict[str, Any] = {
        "filename": filename,
        "snippet": snippet[:METADATA_SNIPPET_MAX_LENGTH],
    }
    index.upsert(vectors=[{"id": screenshot_id, "values": vector, "metadata": metadata}])


async def upsert_screenshot_vector(
    screenshot_id: str,
    vector: list[float],
    filename: str,
    snippet: str,
) -> None:
    await asyncio.to_thread(
        _upsert_vector,
        screenshot_id,
        vector,
        filename,
        snippet,
    )
    logger.info("Upserted Pinecone vector for screenshot %s", screenshot_id)


def _query_vectors(vector: list[float], top_k: int) -> list[tuple[str, float]]:
    index = _get_index()
    response = index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True,
    )
    results: list[tuple[str, float]] = []
    for match in response.matches:
        results.append((match.id, float(match.score)))
    return results


async def query_similar_vectors(
    vector: list[float],
    top_k: int = 10,
) -> list[tuple[str, float]]:
    return await asyncio.to_thread(_query_vectors, vector, top_k)
