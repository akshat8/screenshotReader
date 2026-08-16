# Task 44: README & documentation

**Block:** 7 — Reliability & demo  
**Status:** pending  
**Depends on:** Task 42

## Objective

Document setup, architecture, and trade-offs for reviewers and demo.

## Steps

1. Root `README.md`:
   - Product overview
   - Stack (MongoDB, Pinecone, OpenRouter, local uploads)
   - Setup: `MONGODB_URI` (local or Atlas), env vars, backend, frontend
   - How to run demo
   - Link to [tasks/CONVENTIONS.md](../../CONVENTIONS.md)
2. `backend/README.md` — API summary, dev commands, single `requirements.txt`
3. Link to `tasks/ARCHITECTURE.md` and PRD
4. Document trade-offs:
   - Local disk vs GridFS/S3
   - Pinecone vs pgvector
   - OpenRouter free models vs paid
   - BackgroundTasks vs Celery
5. Do **not** document Docker or pytest (not used in this project)

## Acceptance criteria

- [ ] New developer can run app from README alone
- [ ] Architecture diagram included (text or image)
- [ ] All env vars documented in `.env.example`
- [ ] Demo steps listed
- [ ] Conventions documented in `tasks/CONVENTIONS.md`

## Checkpoint

**Block 7 complete — MVP done:** All PRD Definition of Done items satisfied (except automated tests — out of scope).
