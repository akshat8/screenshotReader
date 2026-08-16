# Task 11: GET list screenshots

**Block:** 2 — Upload & file storage  
**Status:** done  
**Depends on:** Task 09

## Objective

Implement `GET /api/screenshots` for listing all uploads with status.

## Steps

1. Query MongoDB `screenshots` collection
2. Sort by `created_at` descending
3. Response:
   ```json
   {
     "screenshots": [
       { "id": "...", "filename": "...", "status": "completed" }
     ]
   }
   ```
4. Map `processing_status` → `status` in response

## Acceptance criteria

- [ ] Returns all screenshots with id, filename, status
- [ ] Works with 0, 1, and many documents
- [ ] Swagger documents response schema

## Checkpoint

List endpoint for frontend polling (Task 30).
