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

## Hybrid retrieval

```text
final_score = 0.7 × semantic_score (Pinecone) + 0.3 × keyword_score (MongoDB $text)
```

Top 5 → relevance gate → OpenRouter LLM or "not found".

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
RELEVANCE_THRESHOLD=0.35
HYBRID_SEMANTIC_WEIGHT=0.7
HYBRID_KEYWORD_WEIGHT=0.3
TOP_K=5
MAX_UPLOAD_COUNT=50
```
