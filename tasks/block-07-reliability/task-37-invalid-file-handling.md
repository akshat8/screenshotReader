# Task 37: Invalid file handling

**Block:** 7 — Reliability & demo  
**Status:** pending  
**Depends on:** Task 36

## Objective

Handle invalid uploads gracefully on backend and frontend.

## Steps

1. Backend: reject non-image files, oversize files, empty uploads (400)
2. Frontend: filter file input by accept attribute
3. Show user-friendly error message on rejection
4. Do not create Mongo doc or disk file for rejected uploads

## Acceptance criteria

- [ ] PDF/txt upload returns 400
- [ ] UI shows error without crash
- [ ] Valid files in same batch still process if partial upload supported

## Checkpoint

Invalid file test passes.
