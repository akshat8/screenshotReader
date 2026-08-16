# Task 39: LLM unavailable handling

**Block:** 7 — Reliability & demo  
**Status:** pending  
**Depends on:** Task 26

## Objective

Return proper API errors when OpenRouter is down — never fake answers.

## Steps

1. Wrap OpenRouter calls with timeout (e.g. 30s)
2. On failure: return HTTP 503 with message like "Answer service temporarily unavailable"
3. Frontend: show error toast or message, not a fabricated answer
4. Test with invalid API key or network block

## Acceptance criteria

- [ ] No hallucinated answer on LLM failure
- [ ] 503 or 502 returned with clear message
- [ ] UI shows error state

## Checkpoint

LLM outage does not produce misleading answers.
