from itertools import count
from unittest.mock import AsyncMock, patch

import pytest
from langchain_core.messages import AIMessage, ToolMessage

from app.graphs.query_graph import build_query_graph
from app.services.query_agent import (
    CritiqueDecision,
    GoalAssessment,
    GoalPlan,
    GoalStatusUpdate,
)
from app.services.query_service import NOT_FOUND_MESSAGE, execute_query
from app.services.query_tools import ToolObservation
from app.services.retrieval_service import RetrievalHit


SCREENSHOT_ID = "507f1f77bcf86cd799439011"
SCREENSHOT_ID_2 = "507f1f77bcf86cd799439012"
_CALL_IDS = count(1)


def _goal_plan(*goals: str) -> GoalPlan:
    return GoalPlan(goals=list(goals) or ["Find the answer"], reason="Plan.")


def _ai(name: str, **args: str) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": name,
                "args": args,
                "id": f"call-{next(_CALL_IDS)}",
                "type": "tool_call",
            }
        ],
    )


def _script(responses: list[AIMessage]):
    queue = list(responses)

    async def _invoke(messages, tools):
        if not queue:
            raise AssertionError("Agent requested an unexpected tool call")
        return queue.pop(0)

    _invoke.queue = queue
    return _invoke


def _satisfy_all():
    async def _assess(*, goals, **_kwargs):
        return GoalAssessment(
            statuses=[
                GoalStatusUpdate(index=index, status="satisfied", reason="Found.")
                for index in range(len(goals))
            ],
            reason="Updated from the latest tool result.",
        )

    return _assess


def _critique(
    verdict: str,
    *,
    missing_fact: str | None = None,
    revision_guidance: str | None = None,
) -> CritiqueDecision:
    return CritiqueDecision(
        verdict=verdict,
        reason="Critique decision.",
        missing_fact=missing_fact,
        revision_guidance=revision_guidance,
    )


def _hit(
    screenshot_id: str = SCREENSHOT_ID,
    filename: str = "chat.png",
    final_score: float = 0.87,
) -> RetrievalHit:
    return RetrievalHit(
        screenshot_id=screenshot_id,
        filename=filename,
        semantic_score=final_score,
        keyword_score=0.0,
        final_score=final_score,
    )


def _document(
    screenshot_id: str = SCREENSHOT_ID,
    filename: str = "chat.png",
    text: str = "OCR:\n9876543210",
) -> dict:
    return {
        "_id": screenshot_id,
        "filename": filename,
        "searchable_text": text,
    }


def _search_observation(
    hits: list[RetrievalHit],
    *,
    tool_name: str,
    query: str,
) -> ToolObservation:
    if not hits:
        return ToolObservation(
            text=f"{tool_name}({query!r}) returned no screenshots.",
            hits=[],
            documents=[],
        )
    lines = [f"{tool_name}({query!r}) returned {len(hits)} screenshot(s):"]
    for index, hit in enumerate(hits, start=1):
        lines.append(
            f"{index}. id={hit.screenshot_id} filename={hit.filename} "
            f"score={hit.final_score:.3f}"
        )
    return ToolObservation(text="\n".join(lines), hits=hits, documents=[])


def _read_observation(document: dict) -> ToolObservation:
    screenshot_id = str(document["_id"])
    hit = _hit(screenshot_id, document["filename"], 1.0)
    return ToolObservation(
        text=(
            f"read_screenshot({screenshot_id}) loaded "
            f"filename={document['filename']}\n"
            f"Content:\n{document['searchable_text']}"
        ),
        hits=[hit],
        documents=[document],
    )


def _tool_names(result: dict) -> list[str]:
    return [
        item["decision"]
        for item in result["decisions"]
        if item["step"] == "tool_call"
    ]


def test_query_graph_exposes_tool_calling_loop():
    graph = build_query_graph()
    node_names = set(graph.get_graph().nodes)

    assert {
        "plan_goals",
        "agent",
        "tools",
        "assess_goals",
        "reject_early_answer",
        "critique",
    } <= node_names


@pytest.mark.asyncio
async def test_execute_query_give_up_skips_answer_generation():
    with (
        patch(
            "app.graphs.query_graph.plan_goals",
            new_callable=AsyncMock,
            return_value=_goal_plan("Find passport number"),
        ),
        patch(
            "app.graphs.query_graph.invoke_agent_model",
            new=_script([_ai("give_up", reason="No passport screenshot.")]),
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
    assert result["decisions"][0]["step"] == "plan_goals"
    assert _tool_names(result) == ["give_up"]


@pytest.mark.asyncio
async def test_execute_query_answers_despite_low_retrieval_score():
    low_hit = _hit(final_score=0.07)
    document = _document()
    with (
        patch(
            "app.graphs.query_graph.plan_goals",
            new_callable=AsyncMock,
            return_value=_goal_plan("Find phone number"),
        ),
        patch(
            "app.graphs.query_graph.invoke_agent_model",
            new=_script(
                [
                    _ai("semantic_search", query="phone number"),
                    _ai("read_screenshot", screenshot_id=SCREENSHOT_ID),
                    _ai("answer", reason="The number is loaded."),
                ]
            ),
        ),
        patch(
            "app.graphs.query_graph.assess_goals",
            new=_satisfy_all(),
        ),
        patch(
            "app.services.query_tools.run_semantic_search",
            new_callable=AsyncMock,
            return_value=_search_observation(
                [low_hit],
                tool_name="semantic_search",
                query="phone number",
            ),
        ),
        patch(
            "app.services.query_tools.run_read_screenshot",
            new_callable=AsyncMock,
            return_value=_read_observation(document),
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
            return_value="The phone number is 9876543210.",
        ),
        patch(
            "app.graphs.query_graph.critique_answer",
            new_callable=AsyncMock,
            return_value=_critique("accept"),
        ),
    ):
        result = await execute_query("What was the phone number?")

    assert result["found"] is True
    assert "9876543210" in result["answer"]
    assert result["sources"][0]["id"] == SCREENSHOT_ID
    assert result["sources"][0]["relevance"] == 1.0


@pytest.mark.asyncio
async def test_execute_query_selects_keyword_then_semantic_then_answers():
    hit = _hit()
    document = _document()
    searched: list[str] = []
    seen_tools: list[str] = []
    transcripts: list[list] = []

    async def fake_keyword(query: str):
        searched.append(f"keyword:{query}")
        return _search_observation([hit], tool_name="keyword_search", query=query)

    async def fake_semantic(query: str):
        searched.append(f"semantic:{query}")
        return _search_observation([hit], tool_name="semantic_search", query=query)

    async def fake_model(messages, tools):
        transcripts.append(messages)
        seen_tools.extend(tool.name for tool in tools)
        responses = fake_model.responses
        if not responses:
            raise AssertionError("Agent requested an unexpected tool call")
        return responses.pop(0)

    fake_model.responses = [
        _ai("keyword_search", query="9876543210"),
        _ai("semantic_search", query="phone number chat"),
        _ai("read_screenshot", screenshot_id=SCREENSHOT_ID),
        _ai("answer", reason="The number is loaded."),
    ]

    with (
        patch(
            "app.graphs.query_graph.plan_goals",
            new_callable=AsyncMock,
            return_value=_goal_plan("Find phone number"),
        ),
        patch(
            "app.graphs.query_graph.invoke_agent_model",
            new=fake_model,
        ),
        patch(
            "app.graphs.query_graph.assess_goals",
            new=_satisfy_all(),
        ),
        patch(
            "app.services.query_tools.run_keyword_search",
            new_callable=AsyncMock,
            side_effect=fake_keyword,
        ),
        patch(
            "app.services.query_tools.run_semantic_search",
            new_callable=AsyncMock,
            side_effect=fake_semantic,
        ),
        patch(
            "app.services.query_tools.run_read_screenshot",
            new_callable=AsyncMock,
            return_value=_read_observation(document),
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
            return_value="The phone number is 9876543210.",
        ),
        patch(
            "app.graphs.query_graph.critique_answer",
            new_callable=AsyncMock,
            return_value=_critique("accept"),
        ),
    ):
        result = await execute_query("What was the phone number?")

    assert searched == [
        "keyword:9876543210",
        "semantic:phone number chat",
    ]
    assert "semantic_search" in seen_tools
    assert "keyword_search" in seen_tools
    assert "read_screenshot" in seen_tools
    assert "answer" in seen_tools
    assert any(isinstance(message, ToolMessage) for message in transcripts[1])
    assert result["found"] is True
    assert result["sources"][0]["filename"] == "chat.png"
    assert result["decisions"][0]["step"] == "plan_goals"
    assert _tool_names(result) == [
        "keyword_search",
        "semantic_search",
        "read_screenshot",
        "answer",
    ]
    assert any(item["step"] == "goal_status" for item in result["decisions"])
    assert result["decisions"][-1]["decision"] == "accept"


@pytest.mark.asyncio
async def test_execute_query_keeps_searching_while_a_goal_is_open():
    document = _document()
    searches: list[str] = []

    async def fake_assess(*, goals, latest_observation, **_kwargs):
        status = "satisfied" if "9876543210" in latest_observation else "open"
        return GoalAssessment(
            statuses=[
                GoalStatusUpdate(index=0, status=status, reason="Checked the result.")
            ],
            reason="Checked the latest tool result.",
        )

    async def fake_semantic(query: str):
        searches.append(query)
        return _search_observation(
            [_hit()],
            tool_name="semantic_search",
            query=query,
        )

    with (
        patch(
            "app.graphs.query_graph.plan_goals",
            new_callable=AsyncMock,
            return_value=_goal_plan("Find phone number"),
        ),
        patch(
            "app.graphs.query_graph.invoke_agent_model",
            new=_script(
                [
                    _ai("answer", reason="Guessing."),
                    _ai("semantic_search", query="phone number"),
                    _ai("read_screenshot", screenshot_id=SCREENSHOT_ID),
                    _ai("answer", reason="The number is loaded."),
                ]
            ),
        ),
        patch(
            "app.graphs.query_graph.assess_goals",
            new=fake_assess,
        ),
        patch(
            "app.services.query_tools.run_semantic_search",
            new_callable=AsyncMock,
            side_effect=fake_semantic,
        ),
        patch(
            "app.services.query_tools.run_read_screenshot",
            new_callable=AsyncMock,
            return_value=_read_observation(document),
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
            return_value="The phone number is 9876543210.",
        ) as generate_answer,
        patch(
            "app.graphs.query_graph.critique_answer",
            new_callable=AsyncMock,
            return_value=_critique("accept"),
        ),
    ):
        result = await execute_query("What was the phone number?")

    assert searches == ["phone number"]
    generate_answer.assert_awaited_once()
    assert any(item["step"] == "goal_gate" for item in result["decisions"])
    assert result["found"] is True


@pytest.mark.asyncio
async def test_execute_query_critique_search_again_then_accept():
    first_hit = _hit(SCREENSHOT_ID, "calendar.png", 0.2)
    second_hit = _hit(SCREENSHOT_ID_2, "chat.png", 0.9)
    first_doc = _document(SCREENSHOT_ID, "calendar.png", "OCR:\nmeeting at 3pm")
    second_doc = _document(SCREENSHOT_ID_2, "chat.png", "OCR:\n9876543210")
    critiques = [
        _critique("search_again", missing_fact="AC repair phone number"),
        _critique("accept"),
    ]
    semantic_calls: list[str] = []

    async def fake_critique(**_kwargs):
        return critiques.pop(0)

    async def fake_semantic(query: str):
        semantic_calls.append(query)
        if query == "AC repair phone":
            return _search_observation(
                [second_hit],
                tool_name="semantic_search",
                query=query,
            )
        return _search_observation(
            [first_hit],
            tool_name="semantic_search",
            query=query,
        )

    async def fake_read(screenshot_id: str):
        if screenshot_id == SCREENSHOT_ID_2:
            return _read_observation(second_doc)
        return _read_observation(first_doc)

    with (
        patch(
            "app.graphs.query_graph.plan_goals",
            new_callable=AsyncMock,
            return_value=_goal_plan("Find the number"),
        ),
        patch(
            "app.graphs.query_graph.invoke_agent_model",
            new=_script(
                [
                    _ai("semantic_search", query="the number"),
                    _ai("read_screenshot", screenshot_id=SCREENSHOT_ID),
                    _ai("answer", reason="Draft from the calendar."),
                    _ai("semantic_search", query="AC repair phone"),
                    _ai("read_screenshot", screenshot_id=SCREENSHOT_ID_2),
                    _ai("answer", reason="The number is loaded."),
                ]
            ),
        ),
        patch(
            "app.graphs.query_graph.assess_goals",
            new=_satisfy_all(),
        ),
        patch(
            "app.services.query_tools.run_semantic_search",
            new_callable=AsyncMock,
            side_effect=fake_semantic,
        ),
        patch(
            "app.services.query_tools.run_read_screenshot",
            new_callable=AsyncMock,
            side_effect=fake_read,
        ),
        patch(
            "app.graphs.query_graph.get_max_agent_steps",
            return_value=6,
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
            side_effect=[
                "I only see a meeting time.",
                "The phone number is 9876543210.",
            ],
        ) as generate_answer,
        patch(
            "app.graphs.query_graph.critique_answer",
            new_callable=AsyncMock,
            side_effect=fake_critique,
        ),
    ):
        result = await execute_query("What was the number?")

    assert semantic_calls == ["the number", "AC repair phone"]
    assert generate_answer.await_count == 2
    assert result["found"] is True
    assert "9876543210" in result["answer"]
    assert any(
        item["step"] == "goal_status" and "AC repair phone number" in item["decision"]
        for item in result["decisions"]
    )


@pytest.mark.asyncio
async def test_execute_query_multi_step_goals_run_two_searches():
    hit_one = _hit(SCREENSHOT_ID, "invoice.png", 0.8)
    hit_two = _hit(SCREENSHOT_ID_2, "sender.png", 0.7)
    doc_one = _document(SCREENSHOT_ID, "invoice.png", "OCR:\nTotal $42")
    doc_two = _document(SCREENSHOT_ID_2, "sender.png", "OCR:\nFrom: Alex")
    searches: list[str] = []

    async def fake_assess(*, goals, latest_observation, **_kwargs):
        statuses = []
        for index, goal in enumerate(goals):
            status = goal["status"]
            if index == 0 and "Total $42" in latest_observation:
                status = "satisfied"
            if index == 1 and "Alex" in latest_observation:
                status = "satisfied"
            statuses.append(
                GoalStatusUpdate(index=index, status=status, reason="Checked.")
            )
        return GoalAssessment(statuses=statuses, reason="Checked the latest tool result.")

    async def fake_keyword(query: str):
        searches.append(f"keyword:{query}")
        return _search_observation(
            [hit_one],
            tool_name="keyword_search",
            query=query,
        )

    async def fake_semantic(query: str):
        searches.append(f"semantic:{query}")
        return _search_observation(
            [hit_two],
            tool_name="semantic_search",
            query=query,
        )

    async def fake_read(screenshot_id: str):
        if screenshot_id == SCREENSHOT_ID_2:
            return _read_observation(doc_two)
        return _read_observation(doc_one)

    with (
        patch(
            "app.graphs.query_graph.plan_goals",
            new_callable=AsyncMock,
            return_value=_goal_plan("Find invoice total", "Find invoice sender"),
        ),
        patch(
            "app.graphs.query_graph.invoke_agent_model",
            new=_script(
                [
                    _ai("keyword_search", query="invoice total"),
                    _ai("read_screenshot", screenshot_id=SCREENSHOT_ID),
                    _ai("answer", reason="Only the total is loaded."),
                    _ai("semantic_search", query="invoice sender"),
                    _ai("read_screenshot", screenshot_id=SCREENSHOT_ID_2),
                    _ai("answer", reason="Total and sender are loaded."),
                ]
            ),
        ),
        patch(
            "app.graphs.query_graph.assess_goals",
            new=fake_assess,
        ),
        patch(
            "app.services.query_tools.run_keyword_search",
            new_callable=AsyncMock,
            side_effect=fake_keyword,
        ),
        patch(
            "app.services.query_tools.run_semantic_search",
            new_callable=AsyncMock,
            side_effect=fake_semantic,
        ),
        patch(
            "app.services.query_tools.run_read_screenshot",
            new_callable=AsyncMock,
            side_effect=fake_read,
        ),
        patch(
            "app.graphs.query_graph.get_max_agent_steps",
            return_value=6,
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
            return_value="Alex sent an invoice for $42.",
        ),
        patch(
            "app.graphs.query_graph.critique_answer",
            new_callable=AsyncMock,
            return_value=_critique("accept"),
        ),
    ):
        result = await execute_query("Who sent the invoice and what was the total?")

    assert searches == [
        "keyword:invoice total",
        "semantic:invoice sender",
    ]
    assert any(item["step"] == "goal_gate" for item in result["decisions"])
    assert result["found"] is True
    assert "Alex" in result["answer"]
    assert "Find invoice total" in result["decisions"][0]["decision"]


@pytest.mark.asyncio
async def test_execute_query_rejects_unknown_screenshot_id():
    with (
        patch(
            "app.graphs.query_graph.plan_goals",
            new_callable=AsyncMock,
            return_value=_goal_plan("Find the number"),
        ),
        patch(
            "app.graphs.query_graph.invoke_agent_model",
            new=_script(
                [
                    _ai("read_screenshot", screenshot_id="missing"),
                    _ai("give_up", reason="No known screenshot."),
                ]
            ),
        ),
        patch(
            "app.services.query_tools.run_read_screenshot",
            new_callable=AsyncMock,
        ) as read_screenshot,
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
        ) as generate_answer,
    ):
        result = await execute_query("What was the number?")

    read_screenshot.assert_not_awaited()
    generate_answer.assert_not_awaited()
    assert any(item["step"] == "tool_guard" for item in result["decisions"])
    assert result["found"] is False
    assert result["answer"] == NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_execute_query_step_cap_forces_give_up():
    search_calls = 0

    async def fake_semantic(query: str):
        nonlocal search_calls
        search_calls += 1
        return _search_observation(
            [_hit(final_score=0.2)],
            tool_name="semantic_search",
            query=query,
        )

    async def always_search(_messages, _tools):
        return _ai("semantic_search", query="retry")

    with (
        patch(
            "app.graphs.query_graph.plan_goals",
            new_callable=AsyncMock,
            return_value=_goal_plan("Find anything"),
        ),
        patch(
            "app.graphs.query_graph.invoke_agent_model",
            new=always_search,
        ),
        patch(
            "app.graphs.query_graph.assess_goals",
            new=_satisfy_all(),
        ),
        patch(
            "app.services.query_tools.run_semantic_search",
            new_callable=AsyncMock,
            side_effect=fake_semantic,
        ),
        patch(
            "app.graphs.query_graph.get_max_agent_steps",
            return_value=2,
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
        ) as generate_answer,
    ):
        result = await execute_query("What was the number?")

    assert search_calls == 2
    generate_answer.assert_not_awaited()
    assert result["found"] is False
    assert result["answer"] == NOT_FOUND_MESSAGE
    assert any(item["step"] == "step_cap" for item in result["decisions"])


@pytest.mark.asyncio
async def test_execute_query_step_cap_drafts_when_context_is_loaded():
    document = _document()

    async def fake_model(_messages, _tools):
        fake_model.calls += 1
        if fake_model.calls == 1:
            return _ai("semantic_search", query="phone")
        return _ai("read_screenshot", screenshot_id=SCREENSHOT_ID)

    fake_model.calls = 0

    with (
        patch(
            "app.graphs.query_graph.plan_goals",
            new_callable=AsyncMock,
            return_value=_goal_plan("Find phone number"),
        ),
        patch(
            "app.graphs.query_graph.invoke_agent_model",
            new=fake_model,
        ),
        patch(
            "app.graphs.query_graph.assess_goals",
            new=_satisfy_all(),
        ),
        patch(
            "app.services.query_tools.run_semantic_search",
            new_callable=AsyncMock,
            return_value=_search_observation(
                [_hit()],
                tool_name="semantic_search",
                query="phone",
            ),
        ),
        patch(
            "app.services.query_tools.run_read_screenshot",
            new_callable=AsyncMock,
            return_value=_read_observation(document),
        ),
        patch(
            "app.graphs.query_graph.get_max_agent_steps",
            return_value=2,
        ),
        patch(
            "app.graphs.query_graph.generate_answer",
            new_callable=AsyncMock,
            return_value="The phone number is 9876543210.",
        ) as generate_answer,
        patch(
            "app.graphs.query_graph.critique_answer",
            new_callable=AsyncMock,
            return_value=_critique("accept"),
        ),
    ):
        result = await execute_query("What was the phone number?")

    generate_answer.assert_awaited_once()
    assert result["found"] is True
    assert any(item["step"] == "step_cap" for item in result["decisions"])


@pytest.mark.asyncio
async def test_execute_query_asks_clarifying_question():
    with (
        patch(
            "app.graphs.query_graph.plan_goals",
            new_callable=AsyncMock,
            return_value=_goal_plan("Find the number"),
        ),
        patch(
            "app.graphs.query_graph.invoke_agent_model",
            new=_script(
                [_ai("clarify", question="Which repair visit should I look up?")]
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
    assert result["answer"] == "Which repair visit should I look up?"


@pytest.mark.asyncio
async def test_query_endpoint_success(api_client):
    mock_result = {
        "answer": "The phone number is 9876543210.",
        "sources": [
            {
                "id": SCREENSHOT_ID,
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
