from __future__ import annotations

import asyncio
import os
import time
from contextlib import suppress
from typing import Any
from uuid import uuid4

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Internal imports
from hibikasu_agent.agents.parallel_orchestrator.agent import (
    create_coordinator_agent,
    create_parallel_review_agent,
)
from hibikasu_agent.agents.parallel_orchestrator.tools import (
    aggregate_final_issues,
)
from hibikasu_agent.api.schemas import Issue as ApiIssue
from hibikasu_agent.services.runtime import find_issue, set_review_impl
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)

# Module-level holders for chat support (avoid global statements)
_coordinator_agent_holder: list[Any | None] = [None]
_chat_session_service_holder: list[Any | None] = [None]


def install_default_review_impl(app: Any) -> None:  # noqa: PLR0915
    """Initialize ADK review agent and install as runtime review impl.

    This keeps FastAPI app assembly thin; the concrete logic stays here.
    """
    try:
        if os.getenv("HIBIKASU_DISABLE_ADK"):
            logger.info("ADK review integration disabled via HIBIKASU_DISABLE_ADK")
            return
        model_name = os.getenv("ADK_MODEL") or "gemini-2.5-flash-lite"
        logger.info("Initializing ADK parallel review agent", extra={"model": model_name})
        agent = create_parallel_review_agent(model=model_name)
        app.state.adk_parallel_review_agent = agent
        # Coordinator for dialog routing among specialists
        _coordinator_agent_holder[0] = create_coordinator_agent(model=model_name)
        app.state.adk_coordinator_agent = _coordinator_agent_holder[0]

        def _adk_review_impl(prd_text: str) -> list[ApiIssue]:
            try:

                async def _run_once() -> tuple[list[dict], dict]:
                    service = InMemorySessionService()
                    app_name = "hibikasu_review_api"
                    user_id = f"api_user_{uuid4()}"
                    session_id = f"sess_{uuid4()}"

                    await service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
                    runner = Runner(agent=agent, app_name=app_name, session_service=service)

                    content = genai_types.Content(role="user", parts=[genai_types.Part(text=str(prd_text))])
                    async for _event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                        pass

                    sess = await service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
                    state = getattr(sess, "state", {}) if sess else {}
                    out = state.get("final_review_issues") or {}
                    final_issues: list[dict] = []
                    if isinstance(out, dict) and isinstance(out.get("final_issues"), list):
                        final_issues = list(out.get("final_issues") or [])
                    # Return both final_issues and full state for fallback/diagnostics
                    return final_issues, state

                # Apply timeout to avoid hanging background tasks
                timeout_s = float(os.getenv("ADK_REVIEW_TIMEOUT_SEC", "40"))
                logger.info("ADK review run start", extra={"timeout_s": timeout_s})
                _t0 = time.perf_counter()
                final_issues, state = asyncio.run(asyncio.wait_for(_run_once(), timeout=timeout_s))
                _elapsed_ms = int((time.perf_counter() - _t0) * 1000)
                logger.info(
                    "ADK review run done",
                    extra={
                        "final_issues": len(final_issues),
                        "state_keys": list(state.keys()) if isinstance(state, dict) else None,
                        "elapsed_ms": _elapsed_ms,
                    },
                )

                # Fallback: if merger didn't populate final_issues, aggregate locally
                if not final_issues and isinstance(state, dict):
                    try:
                        logger.info("Falling back to local aggregation from specialist outputs")
                        agg = aggregate_final_issues(
                            prd_text=str(prd_text),
                            engineer_issues=state.get("engineer_issues"),
                            ux_designer_issues=state.get("ux_designer_issues"),
                            qa_tester_issues=state.get("qa_tester_issues"),
                            pm_issues=state.get("pm_issues"),
                        )
                        if isinstance(agg, dict) and isinstance(agg.get("final_issues"), list):
                            final_issues = list(agg["final_issues"])
                            logger.info("Local aggregation produced issues", extra={"count": len(final_issues)})
                    except Exception as agg_err:
                        logger.error("Local aggregation failed", extra={"error": str(agg_err)})

                api_issues: list[ApiIssue] = []
                for item in final_issues:
                    try:
                        api_issues.append(
                            ApiIssue(
                                issue_id=str(item.get("issue_id") or ""),
                                priority=int(item.get("priority") or 0),
                                agent_name=str(item.get("agent_name") or "unknown"),
                                comment=str(item.get("comment") or ""),
                                original_text=str(item.get("original_text") or ""),
                            )
                        )
                    except Exception as err:  # validation error on a single item
                        logger.warning("Skipping invalid ADK issue: %s | data=%s", err, item)
                return api_issues
            except Exception as err:
                # Surface nested ExceptionGroup/TaskGroup details if present
                detail = str(err)
                sub = getattr(err, "exceptions", None)
                if isinstance(sub, list | tuple) and sub:
                    detail = f"{detail} | first_sub={sub[0]}"
                # Optionally include stack traces if requested
                include_trace = bool(os.getenv("HIBIKASU_LOG_TRACE"))
                logger.error(
                    "ADK review execution failed",
                    extra={"detail": detail},
                    exc_info=bool(include_trace),
                )
                return [
                    ApiIssue(
                        issue_id="AI-ERROR",
                        priority=1,
                        agent_name="AI-Orchestrator",
                        comment=f"ADK実行に失敗しました: {detail}",
                        original_text=str(prd_text)[:120] or "(empty)",
                    )
                ]

        set_review_impl(_adk_review_impl)
    except Exception as err:
        logger.error("Failed to initialize ADK review integration", extra={"error": str(err)})


async def answer_dialog(review_id: str, issue_id: str, question_text: str) -> str:
    """Answer a follow-up question about a specific issue via coordinator agent.

    Falls back to a heuristic response if coordinator is not initialized.
    """
    try:
        issue = find_issue(review_id, issue_id)
        if issue is None:
            return "該当する論点が見つかりませんでした。"

        coord = _coordinator_agent_holder[0]
        if coord is None:
            # ADK not initialized; fallback response
            return (
                f"（簡易回答）『{issue.original_text}』に関するご質問: {question_text}\n"
                "まずは仕様の明確化と簡潔な対策の合意が有効です。"
            )

        # Lazy init shared session service to accumulate dialog history per issue
        cs = _chat_session_service_holder[0]
        if cs is None:
            cs = InMemorySessionService()
            _chat_session_service_holder[0] = cs

        # Compose runtime context (instruction is owned by coordinator agent via TOML)
        prompt = (
            f"- 担当領域の目安: {issue.agent_name}\n"
            f"- PRD抜粋: {issue.original_text}\n"
            f"- 指摘: {issue.comment}\n\n"
            f"ユーザーの質問: {question_text}"
        )

        session_id = f"dialog_{review_id}_{issue_id}"
        app_name = "hibikasu_review_api"

        async def _run_once() -> str:
            # Ensure session exists (create if missing)
            with suppress(Exception):
                await cs.create_session(app_name=app_name, user_id="dialog_user", session_id=session_id)

            runner = Runner(agent=coord, app_name=app_name, session_service=cs)
            content = genai_types.Content(role="user", parts=[genai_types.Part(text=prompt)])

            final_text = ""
            async for event in runner.run_async(user_id="dialog_user", session_id=session_id, new_message=content):
                if getattr(event, "is_final_response", lambda: False)() and getattr(event, "content", None):
                    event_content = getattr(event, "content", None)
                    if event_content and hasattr(event_content, "parts") and event_content.parts:
                        final_text = event_content.parts[0].text or ""
            return final_text or "回答を生成できませんでした。"

        return await _run_once()
    except Exception as err:
        logger.error("Dialog execution failed", extra={"error": str(err)})
        return "（簡易回答）現在うまく回答できません。時間を置いて再度お試しください。"
