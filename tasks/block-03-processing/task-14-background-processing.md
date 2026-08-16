# Task 14: Background processing service

**Block:** 3 — Processing pipeline  
**Status:** done  
**Depends on:** Task 10

## Objective

Orchestrate screenshot processing using FastAPI `BackgroundTasks`.

## Steps

1. Create `backend/app/services/processing_service.py`
2. Function: `process_screenshot(screenshot_id: str)`
3. Flow:
   - Update status → `processing`
   - Run OCR → Vision → searchable text → embed → Pinecone
   - Update status → `completed` or `failed`
4. Register in upload endpoint via `background_tasks.add_task(...)`

## Acceptance criteria

- [ ] Upload triggers background job
- [ ] Status transitions: `pending/processing` → `completed` or `failed`
- [ ] Errors caught and stored in `processing_error`

## Checkpoint

Processing pipeline skeleton runs end-to-end (stubs OK until Tasks 15–19).
