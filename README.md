# Screenshot Memory

Personal screenshot search: upload images, extract text with OCR + vision, search with hybrid retrieval, get grounded LLM answers with sources.

## Stack

- **Frontend:** React + TypeScript (Block 5+)
- **Backend:** FastAPI + Python
- **Images:** `backend/uploads/` (local disk)
- **Metadata:** MongoDB
- **Vectors:** Pinecone
- **LLM:** OpenRouter (free models)

## Quick start

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set `MONGODB_URI` in `.env` (local MongoDB or [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)).

From repo root:

```bash
uvicorn app.main:app --reload --app-dir backend
```

- Health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### Frontend (Block 5)

```bash
cd frontend
npm install
npm run dev
```

- UI: http://localhost:5173
- Vite proxies `/api` to the backend on port 8000

## Docs

- [Project conventions](tasks/CONVENTIONS.md) — **read before contributing**
- [PRD](Screenshot_Memory_BR_Technical_PRD.md)
- [Architecture](tasks/ARCHITECTURE.md)
- [Implementation tasks](tasks/README.md)
