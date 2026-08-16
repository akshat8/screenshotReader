# Task 13: GET screenshot image

**Block:** 2 — Upload & file storage  
**Status:** done  
**Depends on:** Task 07, Task 12

## Objective

Serve original images for thumbnails and source attribution.

## Steps

1. Implement `GET /api/screenshots/{id}/image`
2. Read file from `file_path` on disk
3. Return `FileResponse` with correct `Content-Type` (image/png, image/jpeg, etc.)
4. Return 404 if file missing or ID invalid

## Acceptance criteria

- [ ] Image loads in browser at `/api/screenshots/{id}/image`
- [ ] Correct content-type header
- [ ] 404 when file or record missing

## Checkpoint

**Block 2 complete:** Upload via Postman → file on disk + Mongo doc + image URL works.
