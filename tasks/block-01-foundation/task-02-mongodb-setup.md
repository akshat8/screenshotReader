# Task 02: MongoDB setup

**Block:** 1 — Foundation  
**Status:** done  
**Depends on:** Task 01

## Objective

Connect to MongoDB using a local install or MongoDB Atlas — **no Docker**.

## Steps

1. Choose one:
   - **Local:** Install MongoDB Community Server and ensure it runs on `localhost:27017`
   - **Atlas:** Create a free cluster and copy the connection string
2. Set `MONGODB_URI` in `backend/.env`:
   ```env
   MONGODB_URI=mongodb://localhost:27017/screenshot_memory
   ```
   Or for Atlas:
   ```env
   MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/screenshot_memory
   ```
3. Verify with `mongosh "<MONGODB_URI>"` or MongoDB Compass
4. Start the API and confirm `/health` shows `mongodb: connected`

## Acceptance criteria

- [ ] `MONGODB_URI` set in `.env`
- [ ] MongoDB reachable from the machine running FastAPI
- [ ] No `docker-compose.yml` in the repo

## Checkpoint

MongoDB available for the FastAPI app via `MONGODB_URI`.
