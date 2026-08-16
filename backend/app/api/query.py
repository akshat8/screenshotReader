import logging

from fastapi import APIRouter, HTTPException

from app.schemas.query import QueryRequest, QueryResponse, QuerySource
from app.services.query_service import execute_query

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def query_screenshots(request: QueryRequest):
    try:
        result = await execute_query(request.query.strip())
        sources = [QuerySource(**source) for source in result["sources"]]
        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            found=result["found"],
        )
    except RuntimeError as exc:
        logger.error("Query failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Answer service temporarily unavailable. Please try again later.",
        )
    except Exception as exc:
        logger.exception("Unexpected query error")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your query.",
        )
