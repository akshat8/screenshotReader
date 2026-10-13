# Architecture — MongoDB + Pinecone + OpenRouter

## Storage layout

```text
User uploads PNG/JPG/WEBP
        │
        ▼
backend/uploads/{id}.png          ← original image (local filesystem)
        │
        ▼
MongoDB screenshots collection      ← metadata, OCR, description, status
        │
        ▼
Pinecone index                      ← embedding vector + minimal metadata
```

## MongoDB document (`screenshots`)

```javascript
{
  _id: ObjectId,
  filename: "IMG_8271.png",
  file_path: "uploads/abc-uuid.png",
  file_hash: "sha256...",
  ocr_text: "...",
  image_description: "...",
  searchable_text: "OCR:\n...\n\nIMAGE DESCRIPTION:\n...",
  processing_status: "pending | processing | completed | failed",
  processing_error: null,
  pinecone_id: "string-id",
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:** `processing_status`, text index on `searchable_text` + `ocr_text`, optional unique `file_hash`.

## Pinecone vector

```json
{
  "id": "screenshot_mongo_id_string",
  "values": [0.12, -0.34, ...],
  "metadata": {
    "filename": "IMG_8271.png",
    "snippet": "first ~500 chars of searchable_text"
  }
}
```

## Query agent (LangGraph + LangChain tools)

```text
plan_goals → agent ⇄ ToolNode(semantic_search | keyword_search | read_screenshot)
                │              → collect → assess_goals
                ↓
         answer → draft → critique → accept | revise | reopen goal
                ↓
         clarify | give_up
```

The chat model is bound to the LangChain tools and the transcript is the
LangGraph message list. `plan_goals` writes 1–3 checklist items. After each
tool result, `assess_goals` marks each item `open`, `satisfied`, or `blocked`.
`answer` is refused while a goal is still open. Critique can revise the draft
or reopen a goal and send the agent back to the tools.

Python enforces bounds (`MAX_AGENT_STEPS`, screenshot ids that already appeared
in a search, one revise / one search-again). Ranking scores are display
metadata, not a yes/no relevance gate.

Search tools use Pinecone (semantic) and MongoDB `$text` (keyword) separately so
the model can choose which to call.

## OpenRouter models (verify at openrouter.ai/models)

| Role | Example free model |
|------|-------------------|
| Vision | `google/gemini-2.0-flash-exp:free` |
| Answer LLM | `meta-llama/llama-3.2-3b-instruct:free` |
| Embeddings | Local `all-MiniLM-L6-v2` (384 dims) recommended |

## Env vars

```env
MONGODB_URI=mongodb://localhost:27017/screenshot_memory
PINECONE_API_KEY=
PINECONE_INDEX_NAME=screenshot-memory
PINECONE_DIMENSION=384
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_VISION_MODEL=google/gemini-2.0-flash-exp:free
OPENROUTER_LLM_MODEL=meta-llama/llama-3.2-3b-instruct:free
EMBEDDING_MODEL=all-MiniLM-L6-v2
UPLOAD_DIR=./uploads
HYBRID_SEMANTIC_WEIGHT=0.7
HYBRID_KEYWORD_WEIGHT=0.3
TOP_K=5
MAX_AGENT_STEPS=4
MAX_UPLOAD_COUNT=50
```
