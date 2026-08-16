from unittest.mock import AsyncMock, patch

import pytest

from app.services.query_service import execute_query, NOT_FOUND_MESSAGE
from app.services.retrieval_service import RetrievalHit


@pytest.mark.asyncio
async def test_execute_query_returns_not_found_when_below_threshold():
    low_score_hit = RetrievalHit(
        screenshot_id="507f1f77bcf86cd799439011",
        filename="test.png",
        semantic_score=0.1,
        keyword_score=0.0,
        final_score=0.07,
    )
    with patch(
        "app.services.query_service.hybrid_search",
        new_callable=AsyncMock,
        return_value=[low_score_hit],
    ):
        result = await execute_query("What is my passport number?")

    assert result["found"] is False
    assert result["sources"] == []
    assert result["answer"] == NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_execute_query_returns_answer_when_relevant():
    hit = RetrievalHit(
        screenshot_id="507f1f77bcf86cd799439011",
        filename="chat.png",
        semantic_score=0.9,
        keyword_score=0.8,
        final_score=0.87,
    )
    context_doc = {
        "_id": "507f1f77bcf86cd799439011",
        "filename": "chat.png",
        "searchable_text": "OCR:\n9876543210",
    }
    with (
        patch(
            "app.services.query_service.hybrid_search",
            new_callable=AsyncMock,
            return_value=[hit],
        ),
        patch(
            "app.services.query_service.get_context_documents",
            new_callable=AsyncMock,
            return_value=[context_doc],
        ),
        patch(
            "app.services.query_service.generate_answer",
            new_callable=AsyncMock,
            return_value="The phone number is 9876543210.",
        ),
    ):
        result = await execute_query("What was the phone number?")

    assert result["found"] is True
    assert "9876543210" in result["answer"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["id"] == "507f1f77bcf86cd799439011"


@pytest.mark.asyncio
async def test_query_endpoint_success(api_client):
    mock_result = {
        "answer": "The phone number is 9876543210.",
        "sources": [
            {
                "id": "507f1f77bcf86cd799439011",
                "filename": "chat.png",
                "relevance": 0.92,
            }
        ],
        "found": True,
    }
    with patch(
        "app.api.query.execute_query",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        response = await api_client.post(
            "/api/query",
            json={"query": "What was the phone number?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["sources"][0]["relevance"] == 0.92


@pytest.mark.asyncio
async def test_query_endpoint_validation_error(api_client):
    response = await api_client.post("/api/query", json={"query": "a"})

    assert response.status_code == 422
