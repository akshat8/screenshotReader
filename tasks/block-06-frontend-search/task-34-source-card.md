# Task 34: SourceCard thumbnails

**Block:** 6 — Frontend search  
**Status:** done  
**Depends on:** Task 33, Task 13

## Objective

Show source screenshot thumbnails below the answer.

## Steps

1. Create `frontend/src/components/SourceCard.tsx`
2. Thumbnail via `getScreenshotImageUrl(id)`
3. Show filename + relevance score
4. Grid or row of source cards
5. Only show when `sources.length > 0`

## Acceptance criteria

- [ ] Thumbnails load for each source
- [ ] Filename and relevance visible
- [ ] Broken image handled gracefully

## Checkpoint

Sources visible under answer for demo query 1 (phone number).
