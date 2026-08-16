# Task 23: Hybrid retrieval merge

**Block:** 4 — Query pipeline  
**Status:** done  
**Depends on:** Task 21, Task 22

## Objective

Combine vector and keyword results with weighted scoring.

## Steps

1. Create `backend/app/services/retrieval_service.py`
2. `hybrid_search(query: str, top_k=5) -> list[{id, filename, final_score, semantic_score, keyword_score}]`
3. Formula:
   ```text
   final_score = 0.7 × semantic_score + 0.3 × keyword_score
   ```
4. Merge by screenshot ID; missing branch scores as 0
5. Sort by `final_score`, return top K (default 5)

## Acceptance criteria

- [ ] Hybrid beats vector-only on phone number query
- [ ] Hybrid beats keyword-only on conceptual query
- [ ] Returns max 5 results with relevance scores

## Checkpoint

`hybrid_search` returns ranked top 5 for demo queries.
