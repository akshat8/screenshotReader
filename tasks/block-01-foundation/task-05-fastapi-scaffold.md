# Task 05: FastAPI scaffold

**Block:** 1 — Foundation  
**Status:** done  
**Depends on:** Task 01

## Objective

Bootstrap the FastAPI application with config, health check, and dependencies.

## Steps

1. Maintain **only** `backend/requirements.txt` (see [CONVENTIONS.md](../../CONVENTIONS.md)):
   ```text
   fastapi
   uvicorn[standard]
   python-multipart
   pydantic-settings
   motor
   pymongo
   pinecone
   sentence-transformers
   easyocr
   httpx
   python-dotenv
   ```
2. Create `backend/app/main.py` with FastAPI app and `/health`
3. Create `backend/app/config.py` using `pydantic-settings` for env vars
4. Create `backend/.env.example` with all required variables
5. Run: `uvicorn app.main:app --reload --app-dir backend`

## Acceptance criteria

- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] Config loads from `.env`
- [ ] Swagger UI at `/docs` works
- [ ] No extra requirements files (`requirements-core.txt`, etc.)

## Checkpoint

FastAPI dev server runs; config pattern established.
