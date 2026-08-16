# Task 21: Pinecone vector search

**Block:** 4 — Query pipeline  
**Status:** done  
**Depends on:** Task 19, Task 18

## Objective

Semantic search over screenshot embeddings.

## Steps

1. In `pinecone_service.py`: `query_vectors(vector, top_k=10) -> list[{id, score}]`
2. Embed user query via `embedding_service`
3. Query Pinecone with cosine similarity
4. Return semantic_score per hit (normalize to 0–1 if needed)

## Acceptance criteria

- [ ] Conceptual query returns relevant screenshot IDs
- [ ] Only `completed` screenshots should be indexed (filter via metadata if added)
- [ ] Returns empty list when index is empty

## Checkpoint

Semantic search returns ranked IDs for test query.
