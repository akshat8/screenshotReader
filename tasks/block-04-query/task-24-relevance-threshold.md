# Task 24: Relevance threshold

**Block:** 4 — Query pipeline  
**Status:** done  
**Depends on:** Task 23

## Objective

Skip LLM when no screenshot is sufficiently relevant (hallucination guard).

## Steps

1. Add `RELEVANCE_THRESHOLD` to config (default `0.35`)
2. If `max(final_score) < threshold`:
   - Return `found: false`
   - Answer: *"I couldn't find enough information in your uploaded screenshots to answer this."*
   - `sources: []`
3. Do not call OpenRouter LLM in this path

## Acceptance criteria

- [ ] Low-relevance query skips LLM
- [ ] Threshold configurable via env
- [ ] Passport-number demo query triggers not-found (Task 40)

## Checkpoint

Relevance gate works before LLM invocation.
