# Task 06: MongoDB connection

**Block:** 1 — Foundation  
**Status:** done  
**Depends on:** Task 02, Task 05

## Objective

Connect FastAPI to MongoDB and define the `screenshots` collection with indexes.

## Steps

1. Create `backend/app/db/mongodb.py`:
   - Motor async client
   - `get_database()` helper
   - Collection name: `screenshots`
2. Create `backend/app/models/screenshot.py` — document shape / Beanie model
3. On startup, create indexes:
   ```javascript
   { processing_status: 1, created_at: -1 }
   { searchable_text: "text", ocr_text: "text" }
   { file_hash: 1 }, unique, sparse  // optional
   ```
4. Add startup hook in `main.py` to verify DB connection
5. Verify insert + read on startup (`verify_mongodb_read_write` in `mongodb.py`) — no pytest (see [CONVENTIONS.md](../../CONVENTIONS.md))

## Acceptance criteria

- [ ] App connects to MongoDB on startup
- [ ] Text index created on `searchable_text` and `ocr_text`
- [ ] Test document insert/read succeeds

## Checkpoint

**Block 1 complete:** FastAPI + MongoDB + Pinecone/OpenRouter env vars configured.
