# Task 40: Not-found query path

**Block:** 7 — Reliability & demo  
**Status:** pending  
**Depends on:** Task 24, Task 33

## Objective

Verify grounded "not found" for questions with no answer in screenshots.

## Steps

1. Demo query: *"What is my passport number?"*
2. Ensure relevance threshold triggers not-found
3. UI shows PRD message, empty sources
4. LLM not called when below threshold

## Acceptance criteria

- [ ] Passport query returns `found: false`
- [ ] No invented passport number in answer
- [ ] Sources array empty

## Checkpoint

Hallucination guard demonstrated in demo.
