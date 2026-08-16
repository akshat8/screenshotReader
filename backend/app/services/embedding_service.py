import logging

from app.config import settings

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading embedding model: %s", settings.embedding_model)
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_text(text: str) -> list[float]:
    normalized_text = (text or "").strip()
    if not normalized_text:
        normalized_text = "empty screenshot"

    model = _get_model()
    vector = model.encode(normalized_text, normalize_embeddings=True)
    return vector.tolist()


def embed_query(query: str) -> list[float]:
    return embed_text(query)
