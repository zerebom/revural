from __future__ import annotations

import os
import time
from collections.abc import Callable
from contextlib import suppress
from uuid import uuid4

from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Internal imports
from hibikasu_agent.agents.parallel_orchestrator.agent import (
    create_coordinator_agent,
    create_parallel_review_agent,
)
from hibikasu_agent.api.schemas.reviews import Issue as ApiIssue
from hibikasu_agent.constants.agents import ROLE_TO_DEFINITION, SPECIALIST_DEFINITIONS
from hibikasu_agent.services.mappers.api_issue_mapper import map_api_issue
from hibikasu_agent.services.providers.adk_session_factory import (
    AdkSessionContext,
    AdkSessionFactory,
)
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


class ADKService:
    """ADKの実行ロジックをカプセル化するサービス"""

    def __init__(self, *, session_factory: AdkSessionFactory | None = None) -> None:
        """
        アプリケーションのライフサイクル中に維持されるステートフルなコンポーネントを初期化する。
        - 対話用コーディネーターエージェント
        - 対話履歴を保持するセッションサービス
        """
        model_name = os.getenv("ADK_MODEL") or "gemini-2.5-flash"
        self._coordinator_agent = create_coordinator_agent(model=model_name)
        self._chat_session_service = InMemorySessionService()  # type: ignore[no-untyped-call]
        self._default_specialist_agents: list[str] = [
            "engineer_specialist",
            "ux_designer_specialist",
            "qa_tester_specialist",
            "pm_specialist",
        ]
        self._session_factory = session_factory or AdkSessionFactory()
        logger.info("ADKService initialized.")

    @property
    def default_review_agents(self) -> list[str]:
        """Returns the default specialist agent names involved in the review."""

        return list(self._default_specialist_agents)

    @property
    def available_agent_roles(self) -> list[str]:
        """Returns available agent roles that can be selected for reviews."""

        return [definition.role for definition in SPECIALIST_DEFINITIONS]

    def get_selected_agent_keys(self, selected_roles: list[str] | None = None) -> list[str]:
        """Convert role names to agent keys, filtering available specialists."""

        if selected_roles is None:
            return self.default_review_agents

        selected_keys = []
        for role in selected_roles:
            if role in ROLE_TO_DEFINITION:
                selected_keys.append(ROLE_TO_DEFINITION[role].agent_key)

        return selected_keys if selected_keys else self.default_review_agents

    async def run_review_async(
        self,
        prd_text: str,
        *,
        on_event: Callable[[Event], None] | None = None,
        selected_agents: list[str] | None = None,
    ) -> list[ApiIssue]:
        """
        PRDのレビューを非同期で実行する。呼び出し毎に独立した ADK セッションを生成・破棄する。

        Args:
            prd_text: レビュー対象のPRDテキスト
            on_event: イベントコールバック関数
            selected_agents: 使用するエージェントのロール一覧（例: ["engineer", "pm"]）
        """
        try:
            model_name = os.getenv("ADK_MODEL") or "gemini-2.5-flash"
            agent = create_parallel_review_agent(model=model_name, selected_agents=selected_agents)

            session_ctx: AdkSessionContext = await self._session_factory.create_session(agent)

            content = genai_types.Content(role="user", parts=[genai_types.Part(text=str(prd_text))])

            # ログ出力：送信されるプロンプト
            logger.info(f"Sending PRD to ADK - length: {len(prd_text)}, agents: {selected_agents}, model: {model_name}")
            logger.info(f"PRD first 500 chars: {prd_text[:500]}")

            _t0 = time.perf_counter()
            async for event in session_ctx.runner.run_async(
                user_id=session_ctx.user_id,
                session_id=session_ctx.session_id,
                new_message=content,
            ):
                # Drain events; optionally hand them to caller for progress updates
                if on_event:
                    try:
                        on_event(event)
                    except Exception as cb_err:
                        logger.warning("on_event callback failed", exc_info=cb_err)
            _elapsed_ms = int((time.perf_counter() - _t0) * 1000)

            sess = await session_ctx.session_service.get_session(
                app_name=session_ctx.app_name,
                user_id=session_ctx.user_id,
                session_id=session_ctx.session_id,
            )
            state = getattr(sess, "state", {}) if sess else {}
            final_review_issues = state.get("final_review_issues")
            if not final_review_issues or not isinstance(final_review_issues, dict):
                logger.error("No final_review_issues in state")
                return []
            final_issues: list[dict[str, object]] = final_review_issues.get("final_issues", [])

            # Expect a typed FinalIssuesResponse object and access directly

            logger.info(
                f"ADK review done - issues: {len(final_issues)}, elapsed: {_elapsed_ms}ms, agents: {selected_agents}"
            )

            # No local aggregation fallback: rely on orchestrator outputs

            api_issues: list[ApiIssue] = []
            for item in final_issues:
                try:
                    api_issue = map_api_issue(item, prd_text)
                    api_issues.append(api_issue)
                except Exception as err:  # validation error on a single item
                    logger.warning("Skipping invalid ADK issue: %s | data=%s", err, item)
            return api_issues
        except Exception as err:  # nosec B110
            logger.error("ADK run failed", extra={"error": str(err)}, exc_info=True)
            raise

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
