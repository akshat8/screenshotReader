# Project Conventions

Follow these rules for all future implementation work in this repository.

## Dependencies

- Use **one** Python requirements file: `backend/requirements.txt`
- Do **not** add `requirements-core.txt`, `requirements-ml.txt`, or other split requirement files
- Add new Python packages only to `backend/requirements.txt`

## Infrastructure

- Do **not** use Docker or `docker-compose.yml` for this project
- MongoDB: local install **or** MongoDB Atlas — configure via `MONGODB_URI` in `backend/.env`
- Verify connectivity with `/health` or MongoDB Compass / `mongosh`

## Testing

- Do **not** add pytest test files, `backend/tests/`, or `pytest.ini`
- Manual verification via Swagger (`/docs`), Postman, or the React UI is sufficient for MVP
- Task 43 (backend tests) is **out of scope**

## Repo layout

```text
screenshotReader/
├── backend/
│   ├── app/
│   ├── uploads/          # gitignored image storage
│   └── requirements.txt  # single requirements file only
├── frontend/
└── tasks/
```

## Environment

- Copy `backend/.env.example` → `backend/.env` (never commit `.env`)
- API keys: Pinecone, OpenRouter — set in `.env` when needed

## Run backend

From repo root:

```bash
uvicorn app.main:app --reload --app-dir backend
```
