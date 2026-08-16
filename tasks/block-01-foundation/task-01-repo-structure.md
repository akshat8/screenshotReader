# Task 01: Repo structure

**Block:** 1 — Foundation  
**Status:** done  
**Depends on:** None

## Objective

Create the monorepo folder layout for backend, frontend, uploads, and tasks.

## Steps

1. Create directories:
   ```text
   screenshotReader/
   ├── backend/
   │   ├── app/
   │   │   ├── api/
   │   │   ├── services/
   │   │   ├── models/
   │   │   ├── schemas/
   │   │   └── db/
   │   ├── uploads/          # gitignored
   │   └── requirements.txt  # single requirements file only
   ├── frontend/
   └── tasks/
   ```
2. Add `.gitignore` entries:
   - `backend/uploads/`
   - `.env`
   - `__pycache__/`, `*.pyc`
   - `node_modules/`, `dist/`
   - `.venv/`
3. Do **not** add `backend/tests/`, `docker-compose.yml`, or split requirement files (see [CONVENTIONS.md](../../CONVENTIONS.md))

## Acceptance criteria

- [ ] All folders exist
- [ ] `backend/uploads/` is gitignored
- [ ] `.env` is gitignored
- [ ] Only `backend/requirements.txt` for Python deps

## Checkpoint

Clean repo structure ready for FastAPI scaffold and MongoDB connection.
