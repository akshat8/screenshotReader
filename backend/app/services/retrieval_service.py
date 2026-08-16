from dataclasses import dataclass
from typing import Any

from app.config import settings
from app.db.mongodb import get_screenshots_collection
from app.models.screenshot import ProcessingStatus
from app.services.embedding_service import embed_query
from app.services.pinecone_service import query_similar_vectors


@dataclass
class RetrievalHit:
    screenshot_id: str
    filename: str
    semantic_score: float
    keyword_score: float
    final_score: float


def _normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    max_score = max(scores.values())
    if max_score <= 0:
        return {key: 0.0 for key in scores}
    return {key: value / max_score for key, value in scores.items()}


async def vector_search(query: str, top_k: int = 10) -> dict[str, float]:
    query_vector = embed_query(query)
    matches = await query_similar_vectors(query_vector, top_k=top_k)
    return {screenshot_id: score for screenshot_id, score in matches}


async def keyword_search(query: str, top_k: int = 10) -> dict[str, float]:
    collection = get_screenshots_collection()
    cursor = (
        collection.find(
            {
                "$text": {"$search": query},
                "processing_status": ProcessingStatus.COMPLETED.value,
            },
            {"score": {"$meta": "textScore"}, "filename": 1},
        )
        .sort([("score", {"$meta": "textScore"})])
        .limit(top_k)
    )

    documents = await cursor.to_list(length=top_k)
    raw_scores = {
        str(document["_id"]): float(document["score"]) for document in documents
    }
    return _normalize_scores(raw_scores)


async def _load_filename_map(screenshot_ids: list[str]) -> dict[str, str]:
    if not screenshot_ids:
        return {}

    from bson import ObjectId
    from bson.errors import InvalidId

    object_ids = []
    for screenshot_id in screenshot_ids:
        try:
            object_ids.append(ObjectId(screenshot_id))
        except InvalidId:
            continue

    if not object_ids:
        return {}

    collection = get_screenshots_collection()
    cursor = collection.find(
        {"_id": {"$in": object_ids}},
        {"filename": 1},
    )
    documents = await cursor.to_list(length=len(object_ids))
    return {str(document["_id"]): document["filename"] for document in documents}


async def hybrid_search(query: str, top_k: int | None = None) -> list[RetrievalHit]:
    top_k = top_k or settings.top_k
    retrieval_pool_size = max(top_k * 2, 10)

    semantic_raw = await vector_search(query, top_k=retrieval_pool_size)
    semantic_scores = _normalize_scores(semantic_raw)

    try:
        keyword_scores = await keyword_search(query, top_k=retrieval_pool_size)
    except Exception:
        keyword_scores = {}

    merged_ids = set(semantic_scores) | set(keyword_scores)
    filename_map = await _load_filename_map(list(merged_ids))

    merged_hits: list[RetrievalHit] = []
    for screenshot_id in merged_ids:
        semantic_score = semantic_scores.get(screenshot_id, 0.0)
        keyword_score = keyword_scores.get(screenshot_id, 0.0)
        final_score = (
            settings.hybrid_semantic_weight * semantic_score
            + settings.hybrid_keyword_weight * keyword_score
        )
        merged_hits.append(
            RetrievalHit(
                screenshot_id=screenshot_id,
                filename=filename_map.get(screenshot_id, "unknown"),
                semantic_score=semantic_score,
                keyword_score=keyword_score,
                final_score=final_score,
            )
        )

    merged_hits.sort(key=lambda hit: hit.final_score, reverse=True)
    return merged_hits[:top_k]


async def get_context_documents(screenshot_ids: list[str]) -> list[dict[str, Any]]:
    from bson import ObjectId
    from bson.errors import InvalidId

    object_ids = []
    for screenshot_id in screenshot_ids:
        try:
            object_ids.append(ObjectId(screenshot_id))
        except InvalidId:
            continue

    if not object_ids:
        return []

    collection = get_screenshots_collection()
    cursor = collection.find(
        {
            "_id": {"$in": object_ids},
            "processing_status": ProcessingStatus.COMPLETED.value,
        }
    )
    return await cursor.to_list(length=len(object_ids))
