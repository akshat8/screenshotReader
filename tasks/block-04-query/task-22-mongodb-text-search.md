# Task 22: MongoDB text search

**Block:** 4 — Query pipeline  
**Status:** done  
**Depends on:** Task 06, Task 17

## Objective

Keyword search for exact entities (phone numbers, prices, IDs).

## Steps

1. In `mongo_service.py` or `retrieval_service.py`:
   ```python
   db.screenshots.find(
     { "$text": { "$search": query }, "processing_status": "completed" },
     { score: { "$meta": "textScore" } }
   ).sort({ score: { "$meta": "textScore" } }).limit(10)
   ```
2. Return `keyword_score` per document (normalize textScore)
3. Test with phone number query from demo dataset

## Acceptance criteria

- [ ] Phone number query ranks correct screenshot
- [ ] Only `completed` documents searched
- [ ] Empty query handled with validation error

## Checkpoint

Keyword search returns hits for exact-match style queries.
