# Task 09: MongoDB doc on upload

**Block:** 2 — Upload & file storage  
**Status:** done  
**Depends on:** Task 08

## Objective

Insert a MongoDB document for each uploaded screenshot.

## Steps

1. On upload, insert document:
   ```javascript
   {
     _id: ObjectId,
     filename: original name,
     file_path: "uploads/{id}.png",
     processing_status: "pending",
     created_at, updated_at
   }
   ```
2. Set `pinecone_id` = string form of `_id`
3. Use Pydantic schemas in `backend/app/schemas/screenshot.py`

## Acceptance criteria

- [ ] Each upload creates one MongoDB document
- [ ] `filename` and `file_path` populated
- [ ] Initial status is `pending` or `processing`

## Checkpoint

Upload creates file on disk + Mongo document.
