# Task 15: OCR service

**Block:** 3 — Processing pipeline  
**Status:** done  
**Depends on:** Task 14

## Objective

Extract text from screenshots using EasyOCR.

## Steps

1. Create `backend/app/services/ocr_service.py`
2. `extract_text(image_path: str) -> str`
3. Use EasyOCR with English (add Hindi if needed for demo screenshots)
4. Handle empty OCR result gracefully (return empty string, not fail)
5. Log OCR failures; let pipeline continue to vision step

## Acceptance criteria

- [ ] OCR returns text from a test screenshot with visible text
- [ ] Empty image returns empty string without crash
- [ ] OCR errors bubble to processing_service as `failed` with message

## Checkpoint

OCR text stored in Mongo `ocr_text` field during processing.
