# Task 29: ScreenshotUploader

**Block:** 5 — Frontend upload  
**Status:** done  
**Depends on:** Task 28

## Objective

Multi-file upload UI with file selection and drop zone.

## Steps

1. Create `frontend/src/components/ScreenshotUploader.tsx`
2. Accept PNG, JPG, JPEG, WEBP
3. Max 50 files per batch
4. "Select Screenshots" button + optional drag-and-drop
5. On submit, call `uploadScreenshots(files)`
6. Show upload in progress state

## Acceptance criteria

- [ ] Multiple files selectable
- [ ] Invalid types rejected in UI
- [ ] Upload triggers API call successfully
- [ ] User feedback during upload

## Checkpoint

User can upload files from browser UI.
