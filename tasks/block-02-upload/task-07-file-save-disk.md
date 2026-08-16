# Task 07: Save files to disk

**Block:** 2 — Upload & file storage  
**Status:** done  
**Depends on:** Task 05, Task 06

## Objective

Save uploaded screenshot bytes to `backend/uploads/` with a stable path scheme.

## Steps

1. Ensure `UPLOAD_DIR` in config (default `./uploads`)
2. Create `backend/app/services/file_service.py`:
   - `save_upload(file_bytes, screenshot_id, extension) -> file_path`
   - Path format: `uploads/{id}.{ext}`
   - Create directory if missing
3. Validate extension: `png`, `jpg`, `jpeg`, `webp`
4. Optional: max file size check (e.g. 10 MB)

## Acceptance criteria

- [ ] Files saved under `backend/uploads/`
- [ ] Returned `file_path` stored relative to backend root
- [ ] Invalid extensions rejected before save

## Checkpoint

Helper can save a test image and return path.
