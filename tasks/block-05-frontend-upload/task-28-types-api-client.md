# Task 28: Types and API client

**Block:** 5 — Frontend upload  
**Status:** done  
**Depends on:** Task 27

## Objective

Define TypeScript types and Axios API client for backend.

## Steps

1. Create `frontend/src/types/screenshot.ts`:
   - `Screenshot`, `UploadResponse`, `QueryRequest`, `QueryResponse`, `Source`
2. Create `frontend/src/services/api.ts`:
   - `uploadScreenshots(files)`
   - `getScreenshots()`
   - `getScreenshot(id)`
   - `getScreenshotImageUrl(id)`
   - `queryScreenshots(query)`
3. Base URL from env: `VITE_API_BASE_URL`

## Acceptance criteria

- [ ] All API methods typed
- [ ] Errors propagated to UI layer
- [ ] Image URL helper returns correct path

## Checkpoint

API client can call all backend endpoints from browser console test.
