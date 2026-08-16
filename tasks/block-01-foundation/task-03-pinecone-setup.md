# Task 03: Pinecone setup

**Block:** 1 — Foundation  
**Status:** done  
**Depends on:** Task 01

## Objective

Create a Pinecone serverless index for screenshot embeddings.

## Steps

1. Sign up at [pinecone.io](https://www.pinecone.io/)
2. Create serverless index:
   - **Name:** `screenshot-memory`
   - **Dimension:** `384` (for `all-MiniLM-L6-v2`)
   - **Metric:** cosine
3. Copy API key to `.env`:
   ```env
   PINECONE_API_KEY=your-key
   PINECONE_INDEX_NAME=screenshot-memory
   PINECONE_DIMENSION=384
   ```
4. Document index name and dimension in `tasks/ARCHITECTURE.md` if changed.

## Acceptance criteria

- [ ] Pinecone index exists with correct dimension
- [ ] API key stored in `.env` (not committed)
- [ ] Index visible in Pinecone console

## Checkpoint

Pinecone index ready for vector upsert (Task 19).
