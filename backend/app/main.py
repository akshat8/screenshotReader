import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.mongodb import (
    close_mongodb_connection,
    connect_to_mongodb,
    init_indexes,
    verify_mongodb_read_write,
)
from app.api.screenshots import router as screenshots_router
from app.api.query import router as query_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    await connect_to_mongodb(settings.mongodb_uri)
    await init_indexes()
    read_write_ok = await verify_mongodb_read_write()
    if not read_write_ok:
        raise RuntimeError("MongoDB read/write verification failed")
    logger.info("MongoDB read/write verification passed")
    yield
    await close_mongodb_connection()


app = FastAPI(
    title="Screenshot Memory API",
    description="Personal screenshot search with OCR, hybrid retrieval, and grounded LLM answers.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(screenshots_router, prefix="/api/screenshots", tags=["screenshots"])
app.include_router(query_router, prefix="/api/query", tags=["query"])


@app.get("/health")
async def health_check():
    try:
        from app.db.mongodb import get_database

        await get_database().command("ping")
        return {
            "status": "ok",
            "mongodb": "connected",
            "pinecone_configured": bool(settings.pinecone_api_key),
            "openrouter_configured": bool(settings.openrouter_api_key),
        }
    except Exception as exc:
        logger.exception("Health check failed")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "mongodb": "disconnected", "detail": str(exc)},
        )
