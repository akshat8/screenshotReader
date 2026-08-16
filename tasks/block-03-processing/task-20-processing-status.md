# Task 20: Processing success/failure status

**Block:** 3 — Processing pipeline  
**Status:** done  
**Depends on:** Task 14, Task 19

## Objective

Finalize status handling for the full processing pipeline.

## Steps

1. On success:
   - `processing_status = completed`
   - Clear `processing_error`
   - Set `updated_at`
2. On failure (OCR, vision, embed, Pinecone):
   - `processing_status = failed`
   - `processing_error = str(exception)` (no secrets in message)
3. Test: 3 images upload → all reach `completed`
4. Test: corrupt file → `failed` with error message

## Acceptance criteria

- [ ] Successful pipeline sets `completed`
- [ ] Any step failure sets `failed` + error
- [ ] Partial Pinecone upsert does not leave orphan vectors without Mongo doc

## Checkpoint

**Block 3 complete:** Upload 3 images → all `completed`; vectors in Pinecone.
