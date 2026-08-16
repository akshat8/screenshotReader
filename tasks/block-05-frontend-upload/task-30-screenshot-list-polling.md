# Task 30: ScreenshotList polling

**Block:** 5 — Frontend upload  
**Status:** done  
**Depends on:** Task 28, Task 29

## Objective

List uploaded screenshots and poll while any are processing.

## Steps

1. Create `frontend/src/components/ScreenshotList.tsx`
2. Fetch `getScreenshots()` on mount and after upload
3. Poll every 2–3 seconds while any status is `processing` or `pending`
4. Stop polling when all `completed` or `failed`
5. Display filename + status per row

## Acceptance criteria

- [ ] List updates without manual refresh
- [ ] Polling stops when processing complete
- [ ] No `setTimeout` abuse — use interval with cleanup on unmount

## Checkpoint

Status changes from processing → completed visible in UI.
