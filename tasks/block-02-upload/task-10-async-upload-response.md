# Task 10: Async upload response

**Block:** 2 — Upload & file storage  
**Status:** done  
**Depends on:** Task 09

## Objective

Return immediately from upload without waiting for AI processing.

## Steps

1. Response shape:
   ```json
   {
     "uploaded": 2,
     "screenshots": [
       { "id": "...", "filename": "IMG.png", "status": "processing" }
     ]
   }
   ```
2. Queue background processing (stub for now; full pipeline in Block 3)
3. Return 200/202 quickly after save + DB insert

## Acceptance criteria

- [ ] API returns in < 2s for batch upload
- [ ] Response includes id, filename, status per file
- [ ] Background task registered (even if stub)

## Checkpoint

Fast upload response; processing wired in Task 14.
