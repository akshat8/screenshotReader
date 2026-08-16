# Task 41: Duplicate detection (optional)

**Block:** 7 — Reliability & demo  
**Status:** pending  
**Depends on:** Task 09

## Objective

Skip re-indexing exact duplicate screenshots (optional MVP).

## Steps

1. On upload, compute SHA-256 `file_hash`
2. Check Mongo for existing `file_hash`
3. If duplicate: skip processing or return existing ID with message
4. Unique index on `file_hash` (sparse)

## Acceptance criteria

- [ ] Same file uploaded twice does not create duplicate Pinecone vectors
- [ ] User informed duplicate was skipped
- [ ] Task marked optional — skip if time-constrained

## Checkpoint

Duplicate upload handled without duplicate vectors.
