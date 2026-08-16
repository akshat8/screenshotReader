# Task 04: OpenRouter setup

**Block:** 1 — Foundation  
**Status:** done  
**Depends on:** Task 01

## Objective

Configure OpenRouter API access for vision and LLM calls.

## Steps

1. Sign up at [openrouter.ai](https://openrouter.ai/)
2. Create API key
3. Add to `.env`:
   ```env
   OPENROUTER_API_KEY=sk-or-...
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_VISION_MODEL=google/gemini-2.0-flash-exp:free
   OPENROUTER_LLM_MODEL=meta-llama/llama-3.2-3b-instruct:free
   ```
4. Verify free models at [openrouter.ai/models](https://openrouter.ai/models) (`:free` filter)
5. Test a simple chat completion via curl or Postman

## Acceptance criteria

- [ ] API key works for chat completion
- [ ] Vision model identified (multimodal for image description)
- [ ] LLM model identified for answer generation
- [ ] Keys in `.env`, not in source code

## Checkpoint

OpenRouter ready for Task 16 (vision) and Task 25 (LLM).
