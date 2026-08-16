# Task 36: CORS configuration

**Block:** 6 — Frontend search  
**Status:** done  
**Depends on:** Task 35

## Objective

Allow frontend dev server to call FastAPI without CORS errors.

## Steps

1. Add `CORSMiddleware` in `backend/app/main.py`
2. Allow origins: `http://localhost:5173` (Vite default)
3. Allow methods: GET, POST
4. Allow credentials if needed

## Acceptance criteria

- [ ] No CORS errors in browser console
- [ ] Upload and query work from React dev server
- [ ] Production origin documented for future deploy

## Checkpoint

**Block 6 complete:** Full UI flow without Postman.
