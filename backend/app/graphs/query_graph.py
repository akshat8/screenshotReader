"""LangGraph query agent.

The LLM plans goals, calls LangChain tools through a bound chat model, and
LangGraph's ToolNode runs the retrieval tools. Goal status gates the answer.
The message list is the agent's transcript. Python enforces the step cap,
known screenshot ids, and a single revise or search-again.
"""

import logging
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.graphs.query_support import (
    acknowledge_open_tool_calls,
    append_decision,
    build_sources,
    call_args,
    format_transcript,
    last_ai_message,
    merge_documents,
    merge_hits,
    tool_call_reason,
    tool_messages_after_last_ai,
    tool_result_text,
)
from app.graphs.state import QueryState
from app.services.openrouter_service import generate_answer
from app.services.query_agent import (
    add_or_reopen_goal,
    apply_goal_statuses,
    assess_goals,
    critique_answer,
    format_goal_decision,
    format_goals,
    goals_allow_answer,
    goals_from_plan,
    plan_goals,
)
from app.services.query_helpers import NOT_FOUND_MESSAGE, get_max_agent_steps
from app.services.query_model import build_agent_system_prompt, invoke_agent_model
from app.services.query_tools import (
    AGENT_TOOLS,
    RETRIEVAL_TOOL_NAMES,
    RETRIEVAL_TOOLS,
    observation_from_json,
)

logger = logging.getLogger(__name__)

_query_graph = None


def _not_found_update(state: QueryState, messages: list | None = None) -> dict:
    update = {
        "answer": NOT_FOUND_MESSAGE,
        "sources": [],
        "found": False,
        "needs_clarification": False,
        "pending_stop": "",
        "decisions": state.get("decisions") or [],
    }
    if messages:
        update["messages"] = messages
    return update


def _forced_stop(state: QueryState) -> dict:
    has_context = bool(state.get("context_documents"))
    decision = "answer" if has_context else "give_up"
    reason = (
        "Step cap reached with screenshot context loaded."
        if has_context
        else "Step cap reached without screenshot context."
    )
    return {
        "pending_stop": decision,
        "decisions": append_decision(state, "step_cap", decision, reason),
    }


async def plan_goals_node(state: QueryState) -> dict:
    plan = await plan_goals(state["user_query"])
    goals = goals_from_plan(plan)
    return {
        "goals": goals,
        "messages": [HumanMessage(content=state["user_query"])],
        "decisions": append_decision(
            state,
            "plan_goals",
            " | ".join(plan.goals),
            plan.reason,
        ),
        "known_screenshot_ids": [],
        "hits": [],
        "context_documents": [],
        "agent_steps": 0,
        "answer_rejections": 0,
        "revise_count": 0,
        "search_again_count": 0,
        "pending_stop": "",
        "tool_accepted": False,
        "draft_answer": "",
        "revision_guidance": "",
    }


async def agent_node(state: QueryState) -> dict:
    if state.get("agent_steps", 0) >= get_max_agent_steps():
        return _forced_stop(state)

    max_steps = get_max_agent_steps()
    remaining = max_steps - state.get("agent_steps", 0)
    system = SystemMessage(
        content=build_agent_system_prompt(
            goals_text=format_goals(state.get("goals") or []),
            known_screenshot_ids=list(state.get("known_screenshot_ids") or []),
            steps_remaining=remaining,
            max_steps=max_steps,
        )
    )
    response = await invoke_agent_model(
        [system, *(state.get("messages") or [])],
        AGENT_TOOLS,
    )
    tool_calls = getattr(response, "tool_calls", None) or []
    if tool_calls:
        call = tool_calls[0]
        decisions = append_decision(
            state,
            "tool_call",
            call["name"],
            tool_call_reason(call),
        )
        pending = ""
        logger.info("Query agent called tool %s", call["name"])
    else:
        pending = "answer" if state.get("context_documents") else "give_up"
        decisions = append_decision(
            state,
            "tool_call",
            pending,
            "Model returned no tool call.",
        )
    return {
        "messages": [response],
        "decisions": decisions,
        "pending_stop": pending,
    }


def route_after_agent(
    state: QueryState,
) -> Literal[
    "validate_tool",
    "draft_answer",
    "reject_early_answer",
    "clarify",
    "not_found",
]:
    pending = state.get("pending_stop") or ""
    if pending == "answer":
        if state.get("context_documents"):
            return "draft_answer"
        return "not_found"
    if pending == "give_up":
        return "not_found"

    message = last_ai_message(state.get("messages") or [])
    if message is None or not message.tool_calls:
        return "not_found"

    name = message.tool_calls[0]["name"]
    if name in RETRIEVAL_TOOL_NAMES:
        return "validate_tool"
    if name == "clarify":
        return "clarify"
    if name == "give_up":
        return "not_found"
    if name == "answer":
        goals = state.get("goals") or []
        if (
            not goals_allow_answer(goals)
            and state.get("answer_rejections", 0) < 1
            and state.get("agent_steps", 0) < get_max_agent_steps()
        ):
            return "reject_early_answer"
        if not state.get("context_documents"):
            return "not_found"
        return "draft_answer"
    return "not_found"


async def validate_tool_node(state: QueryState) -> dict:
    message = last_ai_message(state.get("messages") or [])
    calls = list(message.tool_calls) if message and message.tool_calls else []
    known = set(state.get("known_screenshot_ids") or [])
    invalid_reason = ""
    for call in calls:
        name = call["name"]
        args = call_args(call)
        if name not in RETRIEVAL_TOOL_NAMES:
            invalid_reason = "Retrieval turns cannot include a stop tool."
            break
        if name in ("semantic_search", "keyword_search"):
            if not str(args.get("query") or "").strip():
                invalid_reason = "Search requires a query."
                break
        if name == "read_screenshot":
            screenshot_id = str(args.get("screenshot_id") or "").strip()
            if not screenshot_id or screenshot_id not in known:
                invalid_reason = (
                    "read_screenshot id was not returned by a prior search."
                )
                break

    if invalid_reason:
        return {
            "messages": [
                ToolMessage(
                    content=invalid_reason,
                    tool_call_id=call["id"],
                    name=call["name"],
                )
                for call in calls
            ],
            "agent_steps": state.get("agent_steps", 0) + 1,
            "tool_accepted": False,
            "decisions": append_decision(
                state,
                "tool_guard",
                calls[0]["name"] if calls else "unknown",
                invalid_reason,
            ),
        }
    return {"tool_accepted": True, "pending_stop": ""}


def route_after_validate(state: QueryState) -> Literal["tools", "agent"]:
    if state.get("tool_accepted"):
        return "tools"
    return "agent"


async def collect_results_node(state: QueryState) -> dict:
    tool_messages = tool_messages_after_last_ai(state.get("messages") or [])
    hits = list(state.get("hits") or [])
    documents = list(state.get("context_documents") or [])
    known = list(state.get("known_screenshot_ids") or [])
    for tool_message in tool_messages:
        try:
            observation = observation_from_json(str(tool_message.content))
        except (TypeError, ValueError):
            continue
        for hit in observation.hits:
            if hit.screenshot_id not in known:
                known.append(hit.screenshot_id)
        hits = merge_hits(hits, observation.hits)
        documents = merge_documents(documents, observation.documents)
    logger.info(
        "Query agent collected %s tool result(s) on step %s",
        len(tool_messages),
        state.get("agent_steps", 0) + max(len(tool_messages), 1),
    )
    return {
        "hits": hits,
        "context_documents": documents,
        "known_screenshot_ids": known,
        "agent_steps": state.get("agent_steps", 0) + max(len(tool_messages), 1),
    }


async def assess_goals_node(state: QueryState) -> dict:
    tool_messages = tool_messages_after_last_ai(state.get("messages") or [])
    observation = "\n\n".join(
        tool_result_text(message.content) for message in tool_messages
    )
    assessment = await assess_goals(
        user_query=state["user_query"],
        goals=state.get("goals") or [],
        latest_observation=observation or "No tool result.",
    )
    goals = apply_goal_statuses(state.get("goals") or [], assessment)
    return {
        "goals": goals,
        "decisions": append_decision(
            state,
            "goal_status",
            format_goal_decision(goals),
            assessment.reason,
        ),
    }


async def reject_early_answer_node(state: QueryState) -> dict:
    open_goals = [
        goal["text"]
        for goal in state.get("goals") or []
        if goal.get("status") == "open"
    ]
    reason = "Open goals remain: " + "; ".join(open_goals)
    acknowledgements = acknowledge_open_tool_calls(
        state.get("messages") or [],
        reason,
    )
    return {
        "messages": acknowledgements,
        "answer_rejections": state.get("answer_rejections", 0) + 1,
        "pending_stop": "",
        "decisions": append_decision(state, "goal_gate", "continue", reason),
    }


async def draft_answer_node(state: QueryState) -> dict:
    acknowledgements = acknowledge_open_tool_calls(
        state.get("messages") or [],
        "Drafting an answer from loaded screenshots.",
    )
    documents = state.get("context_documents") or []
    if not documents:
        update = _not_found_update(state, acknowledgements)
        update["draft_answer"] = ""
        update["critique_verdict"] = "accept"
        return update

    guidance = (state.get("revision_guidance") or "").strip()
    question = state["user_query"]
    if guidance:
        question = (
            f"{state['user_query']}\n\n"
            f"Revision guidance from critique: {guidance}"
        )
    draft = await generate_answer(question, documents)
    update = {
        "draft_answer": draft,
        "revision_guidance": "",
        "pending_stop": "",
    }
    if acknowledgements:
        update["messages"] = acknowledgements
    return update


async def critique_node(state: QueryState) -> dict:
    draft = (state.get("draft_answer") or "").strip()
    if not draft:
        return _not_found_update(state) | {"critique_verdict": "accept"}

    revise_count = state.get("revise_count", 0)
    search_again_count = state.get("search_again_count", 0)
    max_steps = get_max_agent_steps()
    decision = await critique_answer(
        user_query=state["user_query"],
        goals=state.get("goals") or [],
        transcript=format_transcript(state.get("messages") or []),
        draft_answer=draft,
        can_revise=revise_count < 1,
        can_search_again=(
            search_again_count < 1
            and state.get("agent_steps", 0) < max_steps
        ),
    )
    decisions = append_decision(state, "critique", decision.verdict, decision.reason)
    if decision.verdict == "accept":
        return {
            "critique_verdict": "accept",
            "answer": draft,
            "sources": build_sources(state),
            "found": True,
            "needs_clarification": False,
            "decisions": decisions,
        }
    if decision.verdict == "revise":
        return {
            "critique_verdict": "revise",
            "revision_guidance": decision.revision_guidance or "",
            "revise_count": revise_count + 1,
            "decisions": decisions,
        }

    missing_fact = decision.missing_fact or ""
    goals = add_or_reopen_goal(state.get("goals") or [], missing_fact)
    return {
        "critique_verdict": "search_again",
        "goals": goals,
        "search_again_count": search_again_count + 1,
        "answer_rejections": 0,
        "messages": [
            HumanMessage(
                content=(
                    "Critique rejected the draft. This goal is open: "
                    f"{missing_fact}. Search for it before answering."
                )
            )
        ],
        "decisions": decisions,
    }


def route_after_critique(
    state: QueryState,
) -> Literal["draft_answer", "agent", "__end__"]:
    verdict = state.get("critique_verdict")
    if verdict == "revise":
        return "draft_answer"
    if verdict == "search_again":
        return "agent"
    return END


async def clarify_node(state: QueryState) -> dict:
    message = last_ai_message(state.get("messages") or [])
    question = ""
    if message and message.tool_calls:
        question = str(call_args(message.tool_calls[0]).get("question") or "").strip()
    acknowledgements = acknowledge_open_tool_calls(
        state.get("messages") or [],
        "Asking a clarifying question.",
    )
    if not question:
        return _not_found_update(state, acknowledgements)
    return {
        "answer": question[:400],
        "sources": [],
        "found": False,
        "needs_clarification": True,
        "messages": acknowledgements,
        "decisions": state.get("decisions") or [],
    }


async def not_found_node(state: QueryState) -> dict:
    acknowledgements = acknowledge_open_tool_calls(
        state.get("messages") or [],
        "Stopping without an answer.",
    )
    return _not_found_update(state, acknowledgements)


def build_query_graph():
    graph = StateGraph(QueryState)
    graph.add_node("plan_goals", plan_goals_node)
    graph.add_node("agent", agent_node)
    graph.add_node("validate_tool", validate_tool_node)
    graph.add_node("tools", ToolNode(RETRIEVAL_TOOLS))
    graph.add_node("collect_results", collect_results_node)
    graph.add_node("assess_goals", assess_goals_node)
    graph.add_node("reject_early_answer", reject_early_answer_node)
    graph.add_node("draft_answer", draft_answer_node)
    graph.add_node("critique", critique_node)
    graph.add_node("clarify", clarify_node)
    graph.add_node("not_found", not_found_node)

    graph.add_edge(START, "plan_goals")
    graph.add_edge("plan_goals", "agent")
    graph.add_conditional_edges("agent", route_after_agent)
    graph.add_conditional_edges("validate_tool", route_after_validate)
    graph.add_edge("tools", "collect_results")
    graph.add_edge("collect_results", "assess_goals")
    graph.add_edge("assess_goals", "agent")
    graph.add_edge("reject_early_answer", "agent")
    graph.add_edge("draft_answer", "critique")
    graph.add_conditional_edges("critique", route_after_critique)
    graph.add_edge("clarify", END)
    graph.add_edge("not_found", END)
    return graph.compile()


def get_query_graph():
    global _query_graph
    if _query_graph is None:
        _query_graph = build_query_graph()
    return _query_graph
