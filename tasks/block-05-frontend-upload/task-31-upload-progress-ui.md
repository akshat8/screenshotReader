# Task 31: UploadProgress UI

**Block:** 5 — Frontend upload  
**Status:** done  
**Depends on:** Task 30

## Objective

Visual status badges for each uploaded screenshot.

## Steps

1. Create `frontend/src/components/UploadProgress.tsx` (or integrate in ScreenshotList)
2. Status indicators per PRD:
   - ✓ Processed (`completed`)
   - ⏳ Processing (`processing` / `pending`)
   - ✗ Failed (`failed`)
3. Optional: show `processing_error` on failed items (truncated)

## Acceptance criteria

- [ ] All four statuses visually distinct
- [ ] Failed items show error hint
- [ ] Accessible text labels (not color-only)

## Checkpoint

**Block 5 complete:** Upload from UI → list shows processing → completed.
