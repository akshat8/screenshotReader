# Screenshot Memory — Implementation Tasks

Sequential task list for the MVP using **MongoDB**, **Pinecone**, **OpenRouter (free models)**, and **local disk** for screenshot files.

## Project conventions (required)

Read **[CONVENTIONS.md](CONVENTIONS.md)** before starting any task.

| Rule | Policy |
|------|--------|
| Python deps | Single file: `backend/requirements.txt` only |
| Docker | Not used |
| Automated tests | Not used (no `backend/tests/`, no pytest) |
| MongoDB | Local install or Atlas via `MONGODB_URI` |

## Stack summary

| Layer | Technology |
|-------|------------|
| Frontend | React + TypeScript + Axios |
| Backend | Python + FastAPI |
| Image files | `backend/uploads/` (local disk) |
| Metadata + text | MongoDB |
| Embeddings | Pinecone (vectors generated locally or via API) |
| OCR | EasyOCR |
| Vision + LLM | OpenRouter free models |
| Embeddings (recommended) | `sentence-transformers/all-MiniLM-L6-v2` (384 dims, local, free) |

## How to use these tasks

1. Work **in order** — each task lists its dependencies.
2. Mark status in each file: `pending` → `in_progress` → `done` (or `cancelled` if out of scope).
3. Complete the **checkpoint** before moving to the next block.
4. Follow **[CONVENTIONS.md](CONVENTIONS.md)** for all new changes.

## Sequential task index

### Block 1 — Foundation (Day 1 morning)

| # | Task | File |
|---|------|------|
| 01 | Repo structure | [block-01-foundation/task-01-repo-structure.md](block-01-foundation/task-01-repo-structure.md) |
| 02 | MongoDB setup | [block-01-foundation/task-02-mongodb-setup.md](block-01-foundation/task-02-mongodb-setup.md) |
| 03 | Pinecone setup | [block-01-foundation/task-03-pinecone-setup.md](block-01-foundation/task-03-pinecone-setup.md) |
| 04 | OpenRouter setup | [block-01-foundation/task-04-openrouter-setup.md](block-01-foundation/task-04-openrouter-setup.md) |
| 05 | FastAPI scaffold | [block-01-foundation/task-05-fastapi-scaffold.md](block-01-foundation/task-05-fastapi-scaffold.md) |
| 06 | MongoDB connection | [block-01-foundation/task-06-mongodb-connection.md](block-01-foundation/task-06-mongodb-connection.md) |

**Block checkpoint:** FastAPI + MongoDB + env vars for Pinecone/OpenRouter.

---

### Block 2 — Upload & file storage (Day 1 midday)

| # | Task | File |
|---|------|------|
| 07 | Save files to disk | [block-02-upload/task-07-file-save-disk.md](block-02-upload/task-07-file-save-disk.md) |
| 08 | POST upload endpoint | [block-02-upload/task-08-post-upload-endpoint.md](block-02-upload/task-08-post-upload-endpoint.md) |
| 09 | MongoDB doc on upload | [block-02-upload/task-09-mongodb-doc-upload.md](block-02-upload/task-09-mongodb-doc-upload.md) |
| 10 | Async upload response | [block-02-upload/task-10-async-upload-response.md](block-02-upload/task-10-async-upload-response.md) |
| 11 | GET list screenshots | [block-02-upload/task-11-get-list-screenshots.md](block-02-upload/task-11-get-list-screenshots.md) |
| 12 | GET screenshot by ID | [block-02-upload/task-12-get-screenshot-by-id.md](block-02-upload/task-12-get-screenshot-by-id.md) |
| 13 | GET screenshot image | [block-02-upload/task-13-get-screenshot-image.md](block-02-upload/task-13-get-screenshot-image.md) |

**Block checkpoint:** Upload via Postman → file on disk + Mongo doc + image URL works.

---

### Block 3 — Processing pipeline (Day 1 afternoon)

| # | Task | File |
|---|------|------|
| 14 | Background processing service | [block-03-processing/task-14-background-processing.md](block-03-processing/task-14-background-processing.md) |
| 15 | OCR service | [block-03-processing/task-15-ocr-service.md](block-03-processing/task-15-ocr-service.md) |
| 16 | OpenRouter vision | [block-03-processing/task-16-openrouter-vision.md](block-03-processing/task-16-openrouter-vision.md) |
| 17 | Searchable text builder | [block-03-processing/task-17-searchable-text.md](block-03-processing/task-17-searchable-text.md) |
| 18 | Embedding service | [block-03-processing/task-18-embedding-service.md](block-03-processing/task-18-embedding-service.md) |
| 19 | Pinecone upsert | [block-03-processing/task-19-pinecone-upsert.md](block-03-processing/task-19-pinecone-upsert.md) |
| 20 | Processing success/failure | [block-03-processing/task-20-processing-status.md](block-03-processing/task-20-processing-status.md) |

**Block checkpoint:** Upload 3 images → all `completed`; vectors visible in Pinecone.

---

### Block 4 — Query pipeline (Day 1 evening)

| # | Task | File |
|---|------|------|
| 21 | Pinecone vector search | [block-04-query/task-21-pinecone-vector-search.md](block-04-query/task-21-pinecone-vector-search.md) |
| 22 | MongoDB text search | [block-04-query/task-22-mongodb-text-search.md](block-04-query/task-22-mongodb-text-search.md) |
| 23 | Hybrid retrieval merge | [block-04-query/task-23-hybrid-retrieval.md](block-04-query/task-23-hybrid-retrieval.md) |
| 24 | Relevance threshold | [block-04-query/task-24-relevance-threshold.md](block-04-query/task-24-relevance-threshold.md) |
| 25 | OpenRouter LLM answer | [block-04-query/task-25-openrouter-llm-answer.md](block-04-query/task-25-openrouter-llm-answer.md) |
| 26 | POST query endpoint | [block-04-query/task-26-post-query-endpoint.md](block-04-query/task-26-post-query-endpoint.md) |

**Block checkpoint:** Full backend — upload → process → query → answer via API.

---

### Block 5 — Frontend upload (Day 2 morning)

| # | Task | File |
|---|------|------|
| 27 | React scaffold | [block-05-frontend-upload/task-27-react-scaffold.md](block-05-frontend-upload/task-27-react-scaffold.md) |
| 28 | Types and API client | [block-05-frontend-upload/task-28-types-api-client.md](block-05-frontend-upload/task-28-types-api-client.md) |
| 29 | ScreenshotUploader | [block-05-frontend-upload/task-29-screenshot-uploader.md](block-05-frontend-upload/task-29-screenshot-uploader.md) |
| 30 | ScreenshotList polling | [block-05-frontend-upload/task-30-screenshot-list-polling.md](block-05-frontend-upload/task-30-screenshot-list-polling.md) |
| 31 | UploadProgress UI | [block-05-frontend-upload/task-31-upload-progress-ui.md](block-05-frontend-upload/task-31-upload-progress-ui.md) |

**Block checkpoint:** Upload from UI → list shows processing → completed.

---

### Block 6 — Frontend search (Day 2 midday)

| # | Task | File |
|---|------|------|
| 32 | SearchBox | [block-06-frontend-search/task-32-search-box.md](block-06-frontend-search/task-32-search-box.md) |
| 33 | AnswerCard | [block-06-frontend-search/task-33-answer-card.md](block-06-frontend-search/task-33-answer-card.md) |
| 34 | SourceCard thumbnails | [block-06-frontend-search/task-34-source-card.md](block-06-frontend-search/task-34-source-card.md) |
| 35 | Home page layout | [block-06-frontend-search/task-35-home-page.md](block-06-frontend-search/task-35-home-page.md) |
| 36 | CORS configuration | [block-06-frontend-search/task-36-cors.md](block-06-frontend-search/task-36-cors.md) |

**Block checkpoint:** Full UI flow without Postman.

---

### Block 7 — Reliability & demo (Day 2 afternoon)

| # | Task | File |
|---|------|------|
| 37 | Invalid file handling | [block-07-reliability/task-37-invalid-file-handling.md](block-07-reliability/task-37-invalid-file-handling.md) |
| 38 | Processing failure UI | [block-07-reliability/task-38-processing-failure-ui.md](block-07-reliability/task-38-processing-failure-ui.md) |
| 39 | LLM unavailable handling | [block-07-reliability/task-39-llm-unavailable.md](block-07-reliability/task-39-llm-unavailable.md) |
| 40 | Not-found query path | [block-07-reliability/task-40-not-found-query.md](block-07-reliability/task-40-not-found-query.md) |
| 41 | Duplicate detection (optional) | [block-07-reliability/task-41-duplicate-detection.md](block-07-reliability/task-41-duplicate-detection.md) |
| 42 | Demo dataset & queries | [block-07-reliability/task-42-demo-dataset.md](block-07-reliability/task-42-demo-dataset.md) |
| 43 | Backend tests | ~~cancelled~~ — see [CONVENTIONS.md](CONVENTIONS.md) |
| 44 | README & documentation | [block-07-reliability/task-44-readme-documentation.md](block-07-reliability/task-44-readme-documentation.md) |

**Block checkpoint:** MVP demo ready per PRD success criteria.

---

## Reference

- Conventions: [CONVENTIONS.md](CONVENTIONS.md)
- PRD: [Screenshot_Memory_BR_Technical_PRD.md](../Screenshot_Memory_BR_Technical_PRD.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
