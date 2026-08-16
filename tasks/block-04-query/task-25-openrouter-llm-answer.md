# Task 25: OpenRouter LLM answer

**Block:** 4 — Query pipeline  
**Status:** done  
**Depends on:** Task 04, Task 23

## Objective

Generate grounded answers from retrieved screenshot context only.

## Steps

1. Add `generate_answer(query, contexts)` to `openrouter_service.py`
2. Prompt rules (from PRD):
   - Use ONLY provided context
   - Do not invent information
   - Say not found if context insufficient
   - Cite screenshot IDs
   - Keep answer concise
3. Pass OCR + description from top-K Mongo docs as context
4. Use `OPENROUTER_LLM_MODEL`

## Acceptance criteria

- [ ] Answer references correct phone number from context
- [ ] No answer invented when context is empty (threshold handles this)
- [ ] API errors return 503, not fake answers

## Checkpoint

LLM returns grounded answer for AC repair phone demo query.
