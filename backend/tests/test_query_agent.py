import pytest

from app.services.query_agent import (
    CritiqueDecision,
    GoalAssessment,
    GoalPlan,
    GoalStatusUpdate,
    add_or_reopen_goal,
    apply_goal_statuses,
    goals_allow_answer,
    normalize_critique,
    normalize_goal_assessment,
    normalize_goal_plan,
    parse_critique,
    parse_goal_assessment,
    parse_goal_plan,
)


def test_parse_goal_plan_accepts_fenced_json():
    raw = """```json
    {"goals": ["Find the phone number"], "reason": "Single fact."}
    ```"""

    plan = parse_goal_plan(raw)

    assert plan.goals == ["Find the phone number"]


def test_normalize_goal_plan_fills_empty_goals():
    plan = normalize_goal_plan(GoalPlan(goals=[], reason=""))

    assert len(plan.goals) == 1
    assert plan.reason == "No reason provided."


def test_parse_goal_assessment_accepts_object():
    raw = (
        '{"statuses":[{"index":0,"status":"satisfied","reason":"Number is present."}],'
        '"reason":"The read contained the fact."}'
    )

    assessment = parse_goal_assessment(raw)

    assert assessment.statuses[0].status == "satisfied"


def test_normalize_goal_assessment_drops_unknown_index():
    assessment = normalize_goal_assessment(
        GoalAssessment(
            statuses=[
                GoalStatusUpdate(index=3, status="satisfied", reason="Out of range."),
                GoalStatusUpdate(index=0, status="blocked", reason="Not in the shots."),
            ],
            reason="Checked.",
        ),
        goal_count=1,
    )

    assert [item.index for item in assessment.statuses] == [0]
    assert assessment.statuses[0].status == "blocked"


def test_apply_goal_statuses_updates_only_known_goals():
    goals = apply_goal_statuses(
        [{"text": "Find total", "status": "open"}],
        GoalAssessment(
            statuses=[GoalStatusUpdate(index=0, status="satisfied", reason="Found.")],
            reason="Updated.",
        ),
    )

    assert goals == [{"text": "Find total", "status": "satisfied"}]


def test_goals_allow_answer_requires_every_goal_closed():
    open_goals = [
        {"text": "Find total", "status": "satisfied"},
        {"text": "Find sender", "status": "open"},
    ]
    closed_goals = [
        {"text": "Find total", "status": "satisfied"},
        {"text": "Find sender", "status": "blocked"},
    ]

    assert goals_allow_answer(open_goals) is False
    assert goals_allow_answer(closed_goals) is True


def test_add_or_reopen_goal_reopens_matching_text():
    goals = add_or_reopen_goal(
        [{"text": "Find the phone number", "status": "satisfied"}],
        "Find the phone number",
    )

    assert goals == [{"text": "Find the phone number", "status": "open"}]


def test_add_or_reopen_goal_appends_a_new_fact():
    goals = add_or_reopen_goal(
        [{"text": "Find the meeting time", "status": "satisfied"}],
        "AC repair phone number",
    )

    assert goals[1] == {"text": "AC repair phone number", "status": "open"}


def test_normalize_critique_drops_search_again_without_missing_fact():
    decision = normalize_critique(
        CritiqueDecision(verdict="search_again", reason="Incomplete."),
        can_revise=True,
        can_search_again=True,
    )

    assert decision.verdict == "accept"


def test_parse_critique_accepts_object():
    raw = (
        '{"verdict": "revise", "reason": "Missing total.", '
        '"missing_fact": null, "revision_guidance": "Include the total."}'
    )

    decision = parse_critique(raw)

    assert decision.verdict == "revise"
    assert decision.revision_guidance == "Include the total."
