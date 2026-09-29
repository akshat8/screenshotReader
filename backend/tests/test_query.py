from unittest.mock import AsyncMock, patch

import pytest

from app.services.query_planner import RetrievalDecision
from app.services.query_service import execute_query, NOT_FOUND_MESSAGE
from app.services.retrieval_service import RetrievalHit


def _decision(action: str, **kwargs) -> RetrievalDecision:
    return RetrievalDecision(action=action, reason="Planner decision.", **kwargs)


@pytest.mark.asyncio
async def test_execute_query_returns_not_found_when_planner_says_insufficient():
    high_score_hit = RetrievalHit(
        screenshot_id="507f1f77bcf86cd799439011",
        filename="test.png",
        semantic_score=0.9,
        keyword_score=0.8,
        final_score=0.87,
    )
    context_doc = {
        "_id": "507f1f77bcf86cd799439011",
        "filename": "test.png",
        "searchable_text": "OCR:\nunrelated calendar invite",
    }
    with (
        patch(
            "app.graphs.query_graph.hybrid_search",
            new_callable=AsyncMock,
            return_value=[high_score_hit],
        ),
        patch(
            "app.graphs.query_graph.get_context_documents",
            new_callable=AsyncMock,
            return_value=[context_doc],
        ),
        patch(
            "app.graphs.query_graph.plan_retrieval",
            new_callable=AsyncMock,
            return_value=_decision("insufficient"),
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
        ) as generate_answer,
    ):
        result = await execute_query("What is my passport number?")

    generate_answer.assert_not_awaited()
    assert result["found"] is False
    assert result["needs_clarification"] is False
    assert result["sources"] == []
    assert result["answer"] == NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_execute_query_answers_when_planner_says_sufficient_despite_low_score():
    low_score_hit = RetrievalHit(
        screenshot_id="507f1f77bcf86cd799439011",
        filename="chat.png",
        semantic_score=0.1,
        keyword_score=0.0,
        final_score=0.07,
    )
    context_doc = {
        "_id": "507f1f77bcf86cd799439011",
        "filename": "chat.png",
        "searchable_text": "OCR:\n9876543210",
    }
    with (
        patch(
            "app.graphs.query_graph.hybrid_search",
            new_callable=AsyncMock,
            return_value=[low_score_hit],
        ),
        patch(
            "app.graphs.query_graph.get_context_documents",
            new_callable=AsyncMock,
            return_value=[context_doc],
        ),
        patch(
            "app.graphs.query_graph.plan_retrieval",
            new_callable=AsyncMock,
            return_value=_decision("sufficient"),
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
            return_value="The phone number is 9876543210.",
        ),
    ):
        result = await execute_query("What was the phone number?")

    assert result["found"] is True
    assert result["needs_clarification"] is False
    assert "9876543210" in result["answer"]


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
            "app.graphs.query_graph.hybrid_search",
            new_callable=AsyncMock,
            return_value=[hit],
        ),
        patch(
            "app.graphs.query_graph.get_context_documents",
            new_callable=AsyncMock,
            return_value=[context_doc],
        ),
        patch(
            "app.graphs.query_graph.plan_retrieval",
            new_callable=AsyncMock,
            return_value=_decision("sufficient"),
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
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
async def test_execute_query_excludes_sources_without_context_documents():
    valid_hit = RetrievalHit(
        screenshot_id="507f1f77bcf86cd799439011",
        filename="chat.png",
        semantic_score=0.9,
        keyword_score=0.8,
        final_score=0.87,
    )
    stale_hit = RetrievalHit(
        screenshot_id="507f1f77bcf86cd799439012",
        filename="unknown",
        semantic_score=0.7,
        keyword_score=0.0,
        final_score=0.49,
    )
    context_doc = {
        "_id": "507f1f77bcf86cd799439011",
        "filename": "chat.png",
        "searchable_text": "OCR:\n9876543210",
    }
    with (
        patch(
            "app.graphs.query_graph.hybrid_search",
            new_callable=AsyncMock,
            return_value=[valid_hit, stale_hit],
        ),
        patch(
            "app.graphs.query_graph.get_context_documents",
            new_callable=AsyncMock,
            return_value=[context_doc],
        ),
        patch(
            "app.graphs.query_graph.plan_retrieval",
            new_callable=AsyncMock,
            return_value=_decision("sufficient"),
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
            return_value="The phone number is 9876543210.",
        ),
    ):
        result = await execute_query("What was the phone number?")

    assert result["found"] is True
    assert len(result["sources"]) == 1
    assert result["sources"][0]["filename"] == "chat.png"


@pytest.mark.asyncio
async def test_execute_query_asks_clarifying_question():
    hit = RetrievalHit(
        screenshot_id="507f1f77bcf86cd799439011",
        filename="chat.png",
        semantic_score=0.4,
        keyword_score=0.2,
        final_score=0.34,
    )
    with (
        patch(
            "app.graphs.query_graph.hybrid_search",
            new_callable=AsyncMock,
            return_value=[hit],
        ),
        patch(
            "app.graphs.query_graph.get_context_documents",
            new_callable=AsyncMock,
            return_value=[{"_id": hit.screenshot_id, "filename": "chat.png"}],
        ),
        patch(
            "app.graphs.query_graph.plan_retrieval",
            new_callable=AsyncMock,
            return_value=_decision(
                "clarify",
                clarifying_question="Which repair visit should I look up?",
            ),
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
        ) as generate_answer,
    ):
        result = await execute_query("What was the number?")

    generate_answer.assert_not_awaited()
    assert result["found"] is False
    assert result["needs_clarification"] is True
    assert result["sources"] == []
    assert result["answer"] == "Which repair visit should I look up?"


@pytest.mark.asyncio
async def test_execute_query_reformulates_then_answers_original_question():
    first_hit = RetrievalHit(
        screenshot_id="507f1f77bcf86cd799439011",
        filename="calendar.png",
        semantic_score=0.2,
        keyword_score=0.0,
        final_score=0.14,
    )
    second_hit = RetrievalHit(
        screenshot_id="507f1f77bcf86cd799439012",
        filename="chat.png",
        semantic_score=0.9,
        keyword_score=0.8,
        final_score=0.87,
    )
    searched_queries: list[str] = []

    async def fake_search(query: str, top_k: int | None = None):
        searched_queries.append(query)
        if len(searched_queries) == 1:
            return [first_hit]
        return [second_hit]

    async def fake_documents(screenshot_ids: list[str]):
        if screenshot_ids == [second_hit.screenshot_id]:
            return [
                {
                    "_id": second_hit.screenshot_id,
                    "filename": "chat.png",
                    "searchable_text": "OCR:\n9876543210",
                }
            ]
        return [
            {
                "_id": first_hit.screenshot_id,
                "filename": "calendar.png",
                "searchable_text": "OCR:\nmeeting at 3pm",
            }
        ]

    decisions = [
        _decision("reformulate", reformulated_query="AC repair phone number"),
        _decision("sufficient"),
    ]

    async def fake_plan(**_kwargs):
        return decisions.pop(0)

    with (
        patch(
            "app.graphs.query_graph.hybrid_search",
            new_callable=AsyncMock,
            side_effect=fake_search,
        ),
        patch(
            "app.graphs.query_graph.get_context_documents",
            new_callable=AsyncMock,
            side_effect=fake_documents,
        ),
        patch(
            "app.graphs.query_graph.plan_retrieval",
            new_callable=AsyncMock,
            side_effect=fake_plan,
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
            return_value="The phone number is 9876543210.",
        ) as generate_answer,
    ):
        result = await execute_query("What was the number?")

    assert searched_queries == ["What was the number?", "AC repair phone number"]
    generate_answer.assert_awaited_once()
    assert generate_answer.await_args.args[0] == "What was the number?"
    assert result["found"] is True
    assert result["sources"][0]["filename"] == "chat.png"


@pytest.mark.asyncio
async def test_execute_query_stops_reformulating_at_attempt_limit():
    hit = RetrievalHit(
        screenshot_id="507f1f77bcf86cd799439011",
        filename="chat.png",
        semantic_score=0.2,
        keyword_score=0.0,
        final_score=0.14,
    )
    search_calls = 0

    async def fake_search(query: str, top_k: int | None = None):
        nonlocal search_calls
        search_calls += 1
        return [hit]

    async def always_reformulate(**kwargs):
        attempt = kwargs["retrieval_attempt"]
        return _decision(
            "reformulate",
            reformulated_query=f"phone number attempt {attempt}",
        )

    with (
        patch(
            "app.graphs.query_graph.hybrid_search",
            new_callable=AsyncMock,
            side_effect=fake_search,
        ),
        patch(
            "app.graphs.query_graph.get_context_documents",
            new_callable=AsyncMock,
            return_value=[{"_id": hit.screenshot_id, "filename": "chat.png"}],
        ),
        patch(
            "app.graphs.query_graph.plan_retrieval",
            new_callable=AsyncMock,
            side_effect=always_reformulate,
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
        ) as generate_answer,
    ):
        result = await execute_query("What was the number?")

    generate_answer.assert_not_awaited()
    assert search_calls == 2
    assert result["found"] is False
    assert result["answer"] == NOT_FOUND_MESSAGE


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
    assert data["needs_clarification"] is False
    assert data["sources"][0]["relevance"] == 0.92


@pytest.mark.asyncio
async def test_query_endpoint_clarification(api_client):
    mock_result = {
        "answer": "Which repair visit should I look up?",
        "sources": [],
        "found": False,
        "needs_clarification": True,
    }
    with patch(
        "app.api.query.execute_query",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        response = await api_client.post(
            "/api/query",
            json={"query": "What was the number?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["found"] is False
    assert data["needs_clarification"] is True
    assert data["answer"] == "Which repair visit should I look up?"


@pytest.mark.asyncio
async def test_query_endpoint_validation_error(api_client):
    response = await api_client.post("/api/query", json={"query": "a"})

    assert response.status_code == 422
