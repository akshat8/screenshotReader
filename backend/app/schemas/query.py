from typing import List

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)


class QuerySource(BaseModel):
    id: str
    filename: str
    relevance: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[QuerySource]
    found: bool
