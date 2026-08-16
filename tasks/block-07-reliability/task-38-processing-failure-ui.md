# Task 38: Processing failure UI

**Block:** 7 — Reliability & demo  
**Status:** pending  
**Depends on:** Task 31

## Objective

Make processing failures visible in the upload list.

## Steps

1. Ensure `failed` status shows ✗ in list
2. Tooltip or expandable error from `processing_error`
3. Test with intentionally bad image or mock OCR failure
4. Failed items do not appear in query results

## Acceptance criteria

- [ ] Failed screenshots clearly marked in UI
- [ ] Error message available to user (sanitized)
- [ ] Failed docs excluded from hybrid search

## Checkpoint

Failure visible end-to-end in UI.
