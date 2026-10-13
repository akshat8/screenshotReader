# Task 24: Relevance threshold

**Block:** 4 — Query pipeline  
**Status:** superseded  
**Depends on:** Task 23

## Current behavior

The live query path does not use a numeric relevance gate. A LangGraph agent plans sub-goals, selects retrieval tools, and decides whether the screenshots can answer. Ranking scores are display metadata only.

## Historical objective

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
