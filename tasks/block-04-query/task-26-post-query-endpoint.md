# Task 26: POST query endpoint

**Block:** 4 — Query pipeline  
**Status:** done  
**Depends on:** Task 24, Task 25

## Objective

Expose `POST /api/query` as the main search API.

## Steps

1. Create `backend/app/api/query.py`
2. Request: `{ "query": "..." }`
3. Response:
   ```json
   {
     "answer": "...",
     "sources": [{ "id", "filename", "relevance" }],
     "found": true
   }
   ```
4. Pipeline: validate → hybrid search → threshold → LLM → response
5. Register route in `main.py`

## Acceptance criteria

- [ ] Full flow works in Swagger
- [ ] `found: false` for irrelevant queries
- [ ] Sources include relevance scores
- [ ] Query validation (min length, max length)

## Checkpoint

**Block 4 complete:** Backend E2E — upload → process → query → answer via API.
