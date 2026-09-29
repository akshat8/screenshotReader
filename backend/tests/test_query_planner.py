import pytest

from app.services.query_planner import (
    RetrievalDecision,
    normalize_decision,
    parse_retrieval_decision,
)


def test_parse_retrieval_decision_accepts_fenced_json():
    raw = """```json
    {"action": "clarify", "reason": "Ambiguous person.", "reformulated_query": null, "clarifying_question": "Which Alex?"}
    ```"""

    decision = parse_retrieval_decision(raw)

    assert decision.action == "clarify"
    assert decision.clarifying_question == "Which Alex?"


def test_parse_retrieval_decision_rejects_non_json():
    with pytest.raises(ValueError):
        parse_retrieval_decision("I think we should answer.")


def test_normalize_sufficient_without_context_becomes_insufficient():
    decision = normalize_decision(
        RetrievalDecision(action="sufficient", reason="Looks good."),
        search_query="passport number",
        has_context=False,
        retrieval_attempt=1,
        max_attempts=2,
    )

    assert decision.action == "insufficient"


def test_normalize_drops_reformulation_that_repeats_the_search_query():
    decision = normalize_decision(
        RetrievalDecision(
            action="reformulate",
            reason="Try again.",
            reformulated_query="  Passport Number ",
        ),
        search_query="passport number",
        has_context=True,
        retrieval_attempt=1,
        max_attempts=2,
    )

    assert decision.action == "insufficient"
    assert decision.reformulated_query is None


def test_normalize_drops_reformulation_on_final_attempt():
    decision = normalize_decision(
        RetrievalDecision(
            action="reformulate",
            reason="One more try.",
            reformulated_query="AC repair phone",
        ),
        search_query="number",
        has_context=True,
        retrieval_attempt=2,
        max_attempts=2,
    )

    assert decision.action == "insufficient"


def test_normalize_keeps_a_distinct_reformulation():
    decision = normalize_decision(
        RetrievalDecision(
            action="reformulate",
            reason="Query is too vague.",
            reformulated_query="AC repair phone number",
        ),
        search_query="the number",
        has_context=True,
        retrieval_attempt=1,
        max_attempts=2,
    )

    assert decision.action == "reformulate"
    assert decision.reformulated_query == "AC repair phone number"
    assert decision.clarifying_question is None


def test_normalize_clarify_requires_a_question():
    decision = normalize_decision(
        RetrievalDecision(action="clarify", reason="Ambiguous.", clarifying_question="  "),
        search_query="the number",
        has_context=True,
        retrieval_attempt=1,
        max_attempts=2,
    )

    assert decision.action == "insufficient"
