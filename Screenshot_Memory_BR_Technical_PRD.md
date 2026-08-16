# Screenshot Memory — Business Requirements & Technical PRD

## 1. Product Overview

**Product:** Screenshot Memory  
**MVP duration:** 2 days  
**Frontend:** React + TypeScript  
**Backend:** Python + FastAPI  
**Database:** PostgreSQL + pgvector

### One-line product definition

A personal screenshot search system that converts an unorganized collection of screenshots into searchable memory using OCR, image understanding, hybrid retrieval, and an LLM.

---

# 2. Business Requirements

## 2.1 Problem Statement

People frequently take screenshots of information they may need later: WhatsApp messages, phone numbers, addresses, bills, payment confirmations, products, tickets, restaurant recommendations, offers, and documents.

As the number of screenshots grows, finding a specific piece of information becomes difficult.

Example:

> What was the phone number of the AC repair person Rahul recommended?

The information exists somewhere in the screenshots, but the user may spend several minutes manually searching.

## 2.2 Proposed Solution

Build a web application that allows a user to:

1. Upload multiple screenshots.
2. Automatically extract searchable information.
3. Store the extracted information in a searchable index.
4. Ask questions using natural language.
5. Retrieve the most relevant screenshots.
6. Generate an answer based only on retrieved screenshots.
7. Display the source screenshots used for the answer.

**Core value proposition:** Turn an unorganized collection of screenshots into searchable personal memory.

## 2.3 Target User

A single individual with many screenshots who frequently needs to retrieve information from them.

Authentication and multi-user support are out of scope for the MVP.

---

# 3. Primary User Journey

### Step 1 — Upload

User uploads multiple screenshots from the React application.

Supported formats: PNG, JPG/JPEG, WEBP.

MVP limit: maximum 50 screenshots per upload.

### Step 2 — Processing

```text
Screenshot
    |
    +--> OCR
    |
    +--> Image understanding
    |
    +--> Metadata generation
    |
    +--> Embedding
    |
    +--> Search index
```

### Step 3 — Ask

Example:

> What was the phone number of the AC repair person?

### Step 4 — Retrieve and answer

The system retrieves relevant screenshots and generates an answer.

Example:

> The AC repair person's phone number is 9876543210.

Sources are shown below the answer.

---

# 4. Business Requirements

## BR-01 — Screenshot Upload

The system shall allow a user to upload one or multiple screenshots.

The UI shall show filename, processing status, and success/failure status.

## BR-02 — Screenshot Processing

For every screenshot, extract:

### OCR text

```text
Rahul:
AC repair wale ka number
9876543210 hai.
```

### Visual description

```text
WhatsApp conversation containing an AC repair
recommendation and a phone number.
```

## BR-03 — Screenshot Indexing

Store:

- Screenshot ID
- Filename
- Original image path
- OCR text
- Image description
- Upload timestamp
- Embedding
- Processing status

## BR-04 — Natural Language Query

Examples:

- What was the AC repair person's number?
- Find the hotel I was looking at in Jaipur.
- What was the price of the Samsung TV?
- What address did Rahul send?
- Which screenshot contains my flight ticket?

## BR-05 — Relevant Retrieval

Return the top 3–5 relevant screenshots.

## BR-06 — Grounded Answer Generation

The LLM must answer using retrieved screenshot context.

If information is unavailable:

> I couldn't find enough information in your uploaded screenshots to answer this.

The system must not invent information.

## BR-07 — Source Attribution

Every generated answer should show the source screenshots.

---

# 5. Out of Scope

Do not implement these in the 2-day MVP:

- Authentication
- Mobile application
- WhatsApp API integration
- Google Drive integration
- Automatic phone-gallery synchronization
- Notifications
- Multi-user support
- Fine-tuning
- Agentic workflows
- Admin dashboard
- Kubernetes
- Production-scale distributed infrastructure
- Advanced image editing

These can be documented as future improvements.

---

# 6. MVP Success Criteria

1. User uploads 20 screenshots and the system processes them.
2. User asks a question whose answer exists and receives the correct answer plus source screenshot.
3. User asks a question whose answer does not exist and receives a clear "not found" response.
4. Multiple related screenshots are ranked and the most relevant sources are returned.

---

# 7. Technical PRD

## 7.1 Technology Stack

### Frontend

- React
- TypeScript
- Axios
- Plain CSS or lightweight UI library

### Backend

- Python
- FastAPI
- Pydantic

### Database

- PostgreSQL
- pgvector

### AI

Use an LLM for image understanding and answer generation.

Use an embedding model for semantic retrieval.

### OCR

Use a reliable OCR library or API.

---

# 8. High-Level Architecture

```text
                    React
                      |
              +-------+-------+
              |               |
        Upload Screenshots   Ask Question
              |               |
              +-------+-------+
                      |
                   FastAPI
                      |
          +-----------+-----------+
          |                       |
      Upload API              Query API
          |                       |
          v                       v
   Image Processing        Query Embedding
          |                       |
      +---+----+                  |
      |        |                  |
     OCR     Vision               |
      |        |                  |
      +---+----+                  |
          |                       |
          v                       |
    Text + Metadata               |
          |                       |
          v                       |
      Embeddings                  |
          |                       |
          +----------+------------+
                     |
                     v
              PostgreSQL
                + pgvector
                     |
                     v
                  Search
                     |
                     v
                  Top K
                     |
                     v
                    LLM
                     |
                     v
             Answer + Sources
                     |
                     v
                   React
```

---

# 9. Database Design

## screenshots

```sql
CREATE TABLE screenshots (
    id UUID PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    ocr_text TEXT,
    image_description TEXT,
    searchable_text TEXT,
    processing_status VARCHAR(30) NOT NULL,
    processing_error TEXT,
    embedding VECTOR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Choose the vector dimension based on the embedding model actually selected.

Example searchable text:

```text
OCR:
Rahul: AC repair wale ka number 9876543210 hai.

IMAGE DESCRIPTION:
WhatsApp conversation containing an AC repair
recommendation and phone number.
```

---

# 10. API Design

## POST /api/screenshots/upload

Upload one or multiple screenshots.

Request:

```text
multipart/form-data
files[]
```

Response:

```json
{
  "uploaded": 2,
  "screenshots": [
    {
      "id": "123",
      "filename": "IMG_8271.png",
      "status": "processing"
    }
  ]
}
```

The API should return quickly instead of waiting for all AI processing.

## GET /api/screenshots

Return uploaded screenshots and processing status.

Example:

```json
{
  "screenshots": [
    {
      "id": "123",
      "filename": "IMG_8271.png",
      "status": "completed"
    },
    {
      "id": "124",
      "filename": "IMG_8272.png",
      "status": "processing"
    }
  ]
}
```

## GET /api/screenshots/{id}

Return screenshot metadata and allow the frontend to display the original image.

## POST /api/query

Request:

```json
{
  "query": "What was the phone number of the AC repair person?"
}
```

Response:

```json
{
  "answer": "The AC repair person's phone number is 9876543210.",
  "sources": [
    {
      "id": "123",
      "filename": "IMG_8271.png",
      "relevance": 0.92
    }
  ]
}
```

---

# 11. Screenshot Processing Pipeline

```text
Image Upload
     |
     v
Validate image
     |
     v
Save image
     |
     v
Create DB record
     |
     v
Background processing
     |
     +--> OCR
     |
     +--> Vision description
     |
     v
Combine OCR + description
     |
     v
Generate embedding
     |
     v
Store metadata + embedding
     |
     v
Mark COMPLETED
```

For the 2-day MVP, FastAPI BackgroundTasks are sufficient.

Do not introduce Celery, Kafka, RabbitMQ, or another queue unless already comfortable and time remains.

---

# 12. Query Pipeline

```text
User Query
     |
     v
Query validation
     |
     v
Generate query embedding
     |
     +------------------+
     |                  |
     v                  v
Vector Search      Keyword Search
     |                  |
     +--------+---------+
              |
              v
       Combine Results
              |
              v
          Top K = 5
              |
              v
       Relevance check
              |
       +------+------+
       |             |
    Relevant       Not relevant
       |             |
       v             v
      LLM        "Not found"
       |
       v
Answer + Source IDs
```

---

# 13. Hybrid Retrieval

Do not rely only on vector search.

Use:

```text
Vector Search
+
Keyword / PostgreSQL Full Text Search
```

Reason:

Semantic search is good for conceptual queries:

> Who recommended an AC repair person?

Keyword search is often better for exact information:

- phone numbers
- booking IDs
- order IDs
- prices
- names
- dates

For the MVP, combine results using a simple scoring strategy:

```text
final_score =
    0.7 * semantic_score +
    0.3 * keyword_score
```

Tune the weights against a small test dataset if needed.

---

# 14. OCR + Vision Representation

For each image:

```text
OCR text
+
Image description
=
Searchable representation
```

Example:

```text
OCR:
Hotel Taj Palace
Delhi
₹8,500

Image description:
Screenshot of a hotel booking page showing
Taj Palace in Delhi with a price of ₹8,500.
```

Embed the combined representation.

---

# 15. LLM Prompt Requirements

The answer-generation prompt must enforce:

1. Use only supplied context.
2. Do not invent information.
3. If context is insufficient, say so.
4. Return source screenshot IDs.
5. Keep the answer concise.

Conceptual prompt:

```text
You are a personal screenshot search assistant.

Answer the user's question using ONLY the provided
screenshot context.

Rules:
1. Do not use outside knowledge.
2. Do not guess or invent information.
3. If the answer cannot be found, say that the
   information was not found in the uploaded screenshots.
4. Cite the screenshot IDs used for the answer.
5. Keep the answer concise.

Context:
{retrieved_screenshots}

Question:
{user_query}
```

---

# 16. Retrieval Confidence / Hallucination Protection

Before sending results to the LLM, calculate a relevance threshold.

If no result is sufficiently relevant:

```text
I couldn't find enough information in your
uploaded screenshots to answer this.
```

This prevents the LLM from generating an answer from unrelated context.

Make the threshold configurable.

---

# 17. React UI Requirements

Only two major sections are required.

## Upload Section

```text
+------------------------------------------+
| Screenshot Memory                        |
|                                          |
| Drop screenshots here                    |
|                                          |
|       [ Select Screenshots ]              |
|                                          |
+------------------------------------------+

Uploaded Screenshots

IMG_123.png       ✓ Processed
IMG_124.png       ✓ Processed
IMG_125.png       ⏳ Processing
IMG_126.png       ✗ Failed
```

## Search Section

```text
+------------------------------------------+
| Search Your Screenshots                  |
|                                          |
| What was the AC repair person's number? |
|                                  [ Ask ] |
+------------------------------------------+

Answer

The AC repair person's number is
9876543210.

Sources

+----------------+
| Screenshot     |
| thumbnail      |
+----------------+
```

Keep the UI simple. Functionality is more important than visual polish.

---

# 18. React Project Structure

```text
frontend/
|
├── src/
│   ├── components/
│   │   ├── ScreenshotUploader.tsx
│   │   ├── UploadProgress.tsx
│   │   ├── ScreenshotList.tsx
│   │   ├── SearchBox.tsx
│   │   ├── AnswerCard.tsx
│   │   └── SourceCard.tsx
│   │
│   ├── pages/
│   │   └── Home.tsx
│   │
│   ├── services/
│   │   └── api.ts
│   │
│   ├── types/
│   │   └── screenshot.ts
│   │
│   ├── App.tsx
│   └── main.tsx
│
└── package.json
```

---

# 19. FastAPI Project Structure

```text
backend/
|
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── screenshots.py
│   │   └── query.py
│   │
│   ├── services/
│   │   ├── ocr_service.py
│   │   ├── vision_service.py
│   │   ├── embedding_service.py
│   │   ├── retrieval_service.py
│   │   └── llm_service.py
│   │
│   ├── models/
│   │   └── screenshot.py
│   │
│   ├── schemas/
│   │   ├── screenshot.py
│   │   └── query.py
│   │
│   └── db/
│       └── database.py
│
├── tests/
│   ├── test_upload.py
│   ├── test_retrieval.py
│   └── test_query.py
│
├── requirements.txt
└── README.md
```

---

# 20. Two-Day Implementation Plan

## Day 1 — Backend + AI Pipeline

### 09:00–11:00

- Create FastAPI project
- Configure PostgreSQL
- Configure pgvector
- Create screenshot model
- Implement upload endpoint

### 11:00–14:00

Implement:

```text
Image
 ↓
OCR
 ↓
Vision description
 ↓
Searchable text
```

Test on 10–20 screenshots.

### 14:00–17:00

Implement:

```text
Searchable text
 ↓
Embedding
 ↓
pgvector
```

### 17:00–20:00

Implement:

```text
POST /api/query
 ↓
Query embedding
 ↓
Vector search
 ↓
LLM
 ↓
Answer
```

### End-of-Day-1 milestone

The entire backend must work through Swagger/Postman:

```text
Upload screenshots
       ↓
Process
       ↓
Ask question
       ↓
Get answer + sources
```

---

## Day 2 — React + Retrieval + Reliability

### 09:00–12:00

Build React upload UI:

- Multiple file selection
- Upload progress
- Processing status
- Screenshot list

### 12:00–14:00

Build query UI:

- Question input
- Ask button
- Loading state
- Answer display
- Source screenshots

### 14:00–16:00

Implement hybrid retrieval:

```text
Vector Search
+
Keyword Search
```

Add relevance threshold.

### 16:00–18:00

Test failure cases:

- Invalid image
- OCR failure
- AI service failure
- No relevant screenshot
- Unrelated question
- Duplicate screenshots

### 18:00–20:00

Prepare:

- README
- Architecture diagram
- Demo screenshots
- Test questions
- Short demo video
- Technical trade-offs

---

# 21. Engineering Trade-offs

## Why PostgreSQL + pgvector?

Avoid operating separate relational and vector databases for a small MVP.

## Why hybrid search?

Vector search handles semantic meaning while keyword search handles exact entities such as phone numbers and IDs.

## Why background processing?

OCR, vision and embedding calls can take time. Upload APIs should return quickly.

## Why no LangGraph?

There is no meaningful multi-step agentic workflow. A deterministic pipeline is simpler and more reliable.

## Why no Redis/Celery?

The MVP processes a small number of screenshots. FastAPI BackgroundTasks are sufficient for the prototype.

## Why OCR + vision?

OCR captures textual information while vision descriptions capture useful information from screenshots where text extraction is insufficient.

---

# 22. Failure Modes

Handle:

### OCR failure

Mark screenshot as `FAILED` and store the error.

### LLM unavailable

Return an appropriate API error and never create a fake answer.

### No relevant result

Return:

```text
Information not found in uploaded screenshots.
```

### Low-quality screenshot

Allow processing to complete but flag low-confidence extraction if possible.

### Duplicate screenshot

Optional MVP feature: calculate an image hash and avoid indexing exact duplicates.

---

# 23. Testing Strategy

Create a small test dataset of approximately 20 screenshots containing:

- WhatsApp conversations
- product screenshots
- bills
- addresses
- tickets
- payment screenshots
- irrelevant images

Create 10–15 known queries.

Example:

```text
Q1: What was the plumber's phone number?
Q2: Which hotel was recommended?
Q3: What was the TV price?
Q4: What address did Rahul send?
Q5: What time was the flight?
Q6: What was the UPI transaction amount?
Q7: What is my passport number?
```

Q7 should intentionally return "not found."

---

# 24. Definition of Done

- [ ] React can upload multiple screenshots.
- [ ] FastAPI accepts uploaded screenshots.
- [ ] Screenshots are persisted.
- [ ] OCR extraction works.
- [ ] Image description generation works.
- [ ] Embeddings are generated.
- [ ] Embeddings are stored in pgvector.
- [ ] User can ask a natural-language question.
- [ ] Relevant screenshots are retrieved.
- [ ] LLM generates an answer from retrieved context.
- [ ] Source screenshots are returned.
- [ ] Unknown questions do not produce hallucinated answers.
- [ ] Processing failures are visible.
- [ ] README explains architecture and trade-offs.
- [ ] Application can be demonstrated end-to-end.

---

# 25. Future Improvements

Do not implement these in the 2-day MVP:

- Automatic gallery synchronization
- WhatsApp integration
- Google Drive integration
- Duplicate detection improvements
- Advanced filters
- Date-based search
- Person/entity extraction
- Multilingual OCR
- Multimodal embeddings
- User authentication
- Cloud object storage
- Distributed background processing

Potential future architecture:

```text
Mobile App
    |
Automatic Gallery Sync
    |
Object Storage
    |
Message Queue
    |
Worker Pool
    |
OCR + Vision
    |
Embedding Service
    |
PostgreSQL + pgvector
    |
Hybrid Search
    |
Reranker
    |
LLM
```

---

# 26. Recommended Demo

Use 15–20 screenshots.

### Query 1

> What was the AC repair person's phone number?

### Query 2

> Which hotel was recommended in Jaipur?

### Query 3

> What was the price of the Samsung TV?

### Query 4

> What was the address Rahul sent?

### Query 5

> What is my passport number?

The last query should demonstrate the grounded "not found" behavior.

---

# 27. Final MVP Architecture

```text
                         +-------------+
                         |    React    |
                         |             |
                         | Upload      |
                         | Search      |
                         | Results     |
                         +------+------+
                                |
                              HTTP
                                |
                         +------v------+
                         |   FastAPI   |
                         +------+------+
                                |
                 +--------------+--------------+
                 |                             |
          Upload Pipeline                Query Pipeline
                 |                             |
                 v                             v
          OCR / Vision                  Query Embedding
                 |                             |
                 v                             v
          Searchable Text               Hybrid Search
                 |                             |
                 v                             |
             Embedding                        |
                 |                             |
                 +-------------+---------------+
                               |
                               v
                      PostgreSQL + pgvector
                               |
                               v
                         Top K Images
                               |
                               v
                              LLM
                               |
                               v
                       Answer + Sources
                               |
                               v
                             React
```

## Guiding principle

Do not expand the scope beyond this architecture during the two days.

The strongest version of this project demonstrates:

> **Real problem → automated ingestion → intelligent retrieval → grounded answer → source verification → sensible engineering trade-offs.**
