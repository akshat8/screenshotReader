# Task 08: POST upload endpoint

**Block:** 2 — Upload & file storage  
**Status:** done  
**Depends on:** Task 07

## Objective

Implement `POST /api/screenshots/upload` accepting multiple files.

## Steps

1. Create `backend/app/api/screenshots.py`
2. Register route in `main.py`
3. Accept `multipart/form-data` with `files[]`
4. Enforce max 50 files per request (`MAX_UPLOAD_COUNT`)
5. For each file: validate type → generate UUID → save to disk

## Acceptance criteria

- [ ] Endpoint accepts multiple PNG/JPG/WEBP files
- [ ] Rejects more than 50 files
- [ ] Rejects invalid file types with 400
- [ ] Route visible in Swagger

## Checkpoint

Can upload files via Postman/Swagger (Mongo doc in Task 09).
