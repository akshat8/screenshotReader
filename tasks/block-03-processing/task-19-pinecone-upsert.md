# Task 19: Pinecone upsert

**Block:** 3 — Processing pipeline  
**Status:** done  
**Depends on:** Task 03, Task 18

## Objective

Store screenshot embeddings in Pinecone after processing.

## Steps

1. Create `backend/app/services/pinecone_service.py`
2. `upsert_screenshot(id, vector, filename, snippet)`
3. Vector ID = Mongo `pinecone_id` (string `_id`)
4. Metadata: `filename`, `snippet` (first ~500 chars of searchable_text)
5. Call upsert at end of successful processing pipeline

## Acceptance criteria

- [ ] Vector appears in Pinecone console after processing
- [ ] ID matches Mongo document
- [ ] Metadata searchable in Pinecone dashboard

## Checkpoint

End-to-end: one upload → Mongo `completed` + Pinecone vector exists.
