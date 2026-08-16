# Task 16: OpenRouter vision

**Block:** 3 — Processing pipeline  
**Status:** done  
**Depends on:** Task 04, Task 14

## Objective

Generate image descriptions via OpenRouter multimodal model.

## Steps

1. Create `backend/app/services/openrouter_service.py`
2. `describe_image(image_path: str) -> str`
3. Send image (base64 or URL) + prompt:
   > Describe this screenshot in 2–3 sentences. Focus on visible UI, conversations, numbers, and context.
4. Use `OPENROUTER_VISION_MODEL` from config
5. Handle API errors with retries (1 retry) or fail with clear error

## Acceptance criteria

- [ ] Description generated for WhatsApp-style screenshot
- [ ] API key not logged
- [ ] Failures set `processing_error` on document

## Checkpoint

`image_description` populated in Mongo during processing.
