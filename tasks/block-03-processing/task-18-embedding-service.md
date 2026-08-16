# Task 18: Embedding service

**Block:** 3 — Processing pipeline  
**Status:** done  
**Depends on:** Task 17

## Objective

Generate embedding vectors from `searchable_text`.

## Steps

1. Create `backend/app/services/embedding_service.py`
2. Use local `sentence-transformers` with `all-MiniLM-L6-v2` (384 dims)
3. `embed_text(text: str) -> list[float]`
4. `embed_query(query: str) -> list[float]` (same model)
5. Lazy-load model on first use to speed app startup

## Acceptance criteria

- [ ] Vector length matches `PINECONE_DIMENSION` (384)
- [ ] Same model used for documents and queries
- [ ] Empty text handled (skip embed or use placeholder)

## Checkpoint

Embedding function returns consistent 384-dim vectors.
