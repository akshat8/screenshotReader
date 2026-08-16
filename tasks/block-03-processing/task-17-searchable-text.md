# Task 17: Searchable text builder

**Block:** 3 — Processing pipeline  
**Status:** done  
**Depends on:** Task 15, Task 16

## Objective

Combine OCR and vision output into a single searchable representation.

## Steps

1. Add helper in `processing_service.py` or `searchable_text.py`:
   ```text
   OCR:
   {ocr_text}

   IMAGE DESCRIPTION:
   {image_description}
   ```
2. Save to Mongo field `searchable_text`
3. Update `updated_at` timestamp

## Acceptance criteria

- [ ] `searchable_text` contains both OCR and description sections
- [ ] Field saved before embedding step
- [ ] Empty OCR still produces valid searchable text from description

## Checkpoint

Mongo document has full `searchable_text` ready for embed + text index.
