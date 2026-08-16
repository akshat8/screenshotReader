# Task 12: GET screenshot by ID

**Block:** 2 — Upload & file storage  
**Status:** done  
**Depends on:** Task 09

## Objective

Implement `GET /api/screenshots/{id}` for full metadata.

## Steps

1. Validate ID format (ObjectId or UUID string)
2. Return metadata: id, filename, status, ocr_text (optional), image_description (optional), timestamps
3. Return 404 if not found
4. Do not include embedding (stored in Pinecone only)

## Acceptance criteria

- [ ] Returns screenshot metadata by ID
- [ ] 404 for invalid/missing ID
- [ ] Sensitive paths acceptable for single-user MVP

## Checkpoint

Detail endpoint ready for SourceCard (Task 34).
