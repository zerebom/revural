from __future__ import annotations

import os
import time
from contextlib import suppress
from uuid import uuid4

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Internal imports
from hibikasu_agent.agents.parallel_orchestrator.agent import (
    create_coordinator_agent,
    create_parallel_review_agent,
)
from hibikasu_agent.api.schemas import Issue as ApiIssue
from hibikasu_agent.api.schemas import IssueSpan
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


class ADKService:
    """ADKの実行ロジックをカプセル化するサービス"""

    def __init__(self) -> None:
        """
        アプリケーションのライフサイクル中に維持されるステートフルなコンポーネントを初期化する。
        - 対話用コーディネーターエージェント
        - 対話履歴を保持するセッションサービス
        """
        model_name = os.getenv("ADK_MODEL") or "gemini-2.5-flash"
        self._coordinator_agent = create_coordinator_agent(model=model_name)
        self._chat_session_service = InMemorySessionService()
        logger.info("ADKService initialized.")

    async def run_review_async(self, prd_text: str) -> list[ApiIssue]:
        """
        PRDのレビューを非同期で実行する。呼び出し毎に独立した ADK セッションを生成・破棄する。
        """
        try:
            model_name = os.getenv("ADK_MODEL") or "gemini-2.5-flash-lite"
            agent = create_parallel_review_agent(model=model_name)

            service = InMemorySessionService()
            app_name = "hibikasu_review_api"
            user_id = f"api_user_{uuid4()}"
            session_id = f"sess_{uuid4()}"

            await service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
            runner = Runner(agent=agent, app_name=app_name, session_service=service)

            content = genai_types.Content(role="user", parts=[genai_types.Part(text=str(prd_text))])

            _t0 = time.perf_counter()
            async for _event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                # Drain events; the final structured output is in session state
                pass
            _elapsed_ms = int((time.perf_counter() - _t0) * 1000)

            sess = await service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
            state = getattr(sess, "state", {}) if sess else {}
            out = state.get("final_review_issues")

            # Expect a typed FinalIssuesResponse object and access directly
            issues_obj = out.final_issues  # type: ignore[attr-defined]
            final_issues: list[dict] = [item.model_dump() for item in (issues_obj or [])]

            logger.info(
                "ADK review run done",
                extra={
                    "final_issues": len(final_issues),
                    "state_keys": list(state.keys()) if isinstance(state, dict) else None,
                    "elapsed_ms": _elapsed_ms,
                },
            )

            # No local aggregation fallback: rely on orchestrator outputs

            api_issues: list[ApiIssue] = []
            for item in final_issues:
                try:
                    original = str(item.get("original_text") or "")
                    # Compute span best-effort here; AiService will skip if already set
                    span_obj = self._calculate_span(prd_text, original)
                    api_issues.append(
                        ApiIssue(
                            issue_id=str(item.get("issue_id") or ""),
                            priority=int(item.get("priority") or 0),
                            agent_name=str(item.get("agent_name") or "unknown"),
                            comment=str(item.get("comment") or ""),
                            original_text=original,
                            span=span_obj,
                        )
                    )
                except Exception as err:  # validation error on a single item
                    logger.warning("Skipping invalid ADK issue: %s | data=%s", err, item)
            return api_issues
        except Exception as err:  # nosec B110
            detail = str(err)
            sub = getattr(err, "exceptions", None)
            if isinstance(sub, list | tuple) and sub:
                detail = f"{detail} | first_sub={sub[0]}"
            include_trace = bool(os.getenv("HIBIKASU_LOG_TRACE"))
            logger.error("ADK review execution failed", extra={"detail": detail}, exc_info=bool(include_trace))
            return [
                ApiIssue(
                    issue_id="AI-ERROR",
                    priority=1,
                    agent_name="AI-Orchestrator",
                    comment=f"ADK実行に失敗しました: {detail}",
                    original_text=str(prd_text)[:120] or "(empty)",
                )
            ]

    async def answer_dialog_async(self, issue: ApiIssue, question_text: str) -> str:
        """
        特定のIssueに関するユーザーの質問に回答する。初期化時のエージェントと
        セッションサービスを利用して会話の文脈を維持する。
        """
        try:
            coord = self._coordinator_agent
            cs = self._chat_session_service

            # Compose runtime context (instruction is owned by coordinator agent via TOML)
            prompt = (
                f"- 担当領域の目安: {issue.agent_name}\n"
                f"- PRD抜粋: {issue.original_text}\n"
                f"- 指摘: {issue.comment}\n\n"
                f"ユーザーの質問: {question_text}"
            )

            session_id = f"dialog_{uuid4()}"
            app_name = "hibikasu_review_api"

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
        except Exception as err:  # nosec B110
            logger.error("Dialog execution failed", extra={"error": str(err)})
            return "（簡易回答）現在うまく回答できません。時間を置いて再度お試しください。"

    # ----- Internal helpers -----

    def _calculate_span(self, prd_text: str, original_text: str) -> IssueSpan | None:
        """Compute a best-effort span of original_text within prd_text.

        Returns an IssueSpan if found, else None. Uses a simple substring search
        with whitespace-trimmed snippet to avoid trivial mismatches.
        """
        try:
            snippet = (original_text or "").strip()
            if not snippet:
                return None
            start = prd_text.find(snippet)
            if start < 0:
                return None
            return IssueSpan(start_index=start, end_index=start + len(snippet))
        except Exception:  # nosec B110
            return None
