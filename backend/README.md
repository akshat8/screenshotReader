# Screenshot Memory — Backend

FastAPI backend for screenshot upload, processing, and natural-language search.

See [tasks/CONVENTIONS.md](../tasks/CONVENTIONS.md) for project rules (no Docker, no pytest, single `requirements.txt`).

## Prerequisites

- Python 3.11+
- MongoDB (local install or MongoDB Atlas)

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env   # set MONGODB_URI, Pinecone + OpenRouter keys
```

## Processing pipeline (Block 3)

After upload, each screenshot is processed in the background:

1. OCR (EasyOCR)
2. Vision description (OpenRouter)
3. Searchable text + embedding (`BAAI/bge-large-en-v1.5`, 1024 dims)
4. Pinecone vector upsert
5. MongoDB status → `completed` or `failed`

Requires `OPENROUTER_API_KEY` and `PINECONE_API_KEY` in `.env`.

Install ML dependencies:

```bash
pip install -r requirements.txt
```

## Query API (Block 4)

| Method | Path         | Description                                    |
| ------ | ------------ | ---------------------------------------------- |
| POST   | `/api/query` | Natural language search — `{ "query": "..." }` |

Response: `{ "answer", "sources": [{ "id", "filename", "relevance" }], "found" }`

Hybrid retrieval: `0.7 × semantic (Pinecone) + 0.3 × keyword (MongoDB $text)`.

## API (Block 2)

| Method | Path                          | Description                                   |
| ------ | ----------------------------- | --------------------------------------------- |
| POST   | `/api/screenshots/upload`     | Upload one or more images (`files` multipart) |
| GET    | `/api/screenshots`            | List all screenshots with status              |
| GET    | `/api/screenshots/{id}`       | Screenshot metadata                           |
| GET    | `/api/screenshots/{id}/image` | Original image file                           |

## Run

From repo root:

```bash
uvicorn app.main:app --reload --app-dir backend
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Environment

See `.env.example` for MongoDB, Pinecone, and OpenRouter variables.
