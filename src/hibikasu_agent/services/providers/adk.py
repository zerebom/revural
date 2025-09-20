from __future__ import annotations

import os
import re
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
from hibikasu_agent.api.schemas.reviews import IssueSpan
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
        self._chat_session_service = InMemorySessionService()  # type: ignore[no-untyped-call]
        self._default_specialist_agents: list[str] = [
            "engineer_specialist",
            "ux_designer_specialist",
            "qa_tester_specialist",
            "pm_specialist",
        ]
        logger.info("ADKService initialized.")

    @property
    def default_review_agents(self) -> list[str]:
        """Returns the default specialist agent names involved in the review."""

        return list(self._default_specialist_agents)

    def _normalize_text(self, text: str) -> str:
        """テキストから空白文字（スペース、タブ、改行など）をすべて除去する"""
        return re.sub(r"\s+", "", text)

    def _find_simple_span(self, prd_text: str, original_text: str) -> IssueSpan | None:
        """単純な文字列検索でspanを計算"""
        start_index = prd_text.find(original_text)
        if start_index != -1:
            return IssueSpan(
                start_index=start_index,
                end_index=start_index + len(original_text),
            )
        return None

    def _find_normalized_start_index(self, prd_text: str, start_index_normalized: int) -> int:
        """正規化された開始位置を元の文字列インデックスへマップ"""
        if start_index_normalized == 0:
            # 最初の非空白文字を探す
            for i, ch in enumerate(prd_text):
                if not ch.isspace():
                    return i
            return 0

        # 非空白文字を start_index_normalized 個スキップした位置を探す
        non_space_seen = 0
        for i, ch in enumerate(prd_text):
            if not ch.isspace():
                if non_space_seen == start_index_normalized:
                    return i
                non_space_seen += 1
        return -1

    def _find_end_index(self, prd_text: str, start_index: int, target_len: int) -> int:
        """開始位置から target_len 分の非空白文字をカバーする終端位置を計算"""
        covered = 0
        for j in range(start_index, len(prd_text)):
            if not prd_text[j].isspace():
                covered += 1
                if covered >= target_len:
                    return j + 1  # 半開区間のため +1
        return len(prd_text)  # 末尾までに満たない場合

    def _calculate_span(self, prd_text: str, original_text: str) -> IssueSpan | None:
        """original_text を基に prd_text 内の位置情報 (span) を計算する（正規化対応）"""
        if not original_text:
            return None

        # 正規化されたテキストで位置を検索
        prd_normalized = self._normalize_text(prd_text)
        original_normalized = self._normalize_text(original_text)

        if not original_normalized:
            return None

        start_index_normalized = prd_normalized.find(original_normalized)
        if start_index_normalized == -1:
            # 正規化しても見つからない場合は、単純な検索を試す
            return self._find_simple_span(prd_text, original_text)

        # 正規化された開始位置を、元の文字列インデックスへマップ
        actual_start_index = self._find_normalized_start_index(prd_text, start_index_normalized)
        if actual_start_index == -1:
            return None

        # 終端位置を計算
        target_len = len(original_normalized)
        actual_end_index = self._find_end_index(prd_text, actual_start_index, target_len)

        return IssueSpan(start_index=actual_start_index, end_index=actual_end_index)

    def _create_api_issue(self, item: dict[str, object], prd_text: str) -> ApiIssue:
        """Create ApiIssue from raw ADK output item."""
        original_text = str(item.get("original_text") or "")
        span = self._calculate_span(prd_text, original_text)
        logger.info(f"ADK issue span: {span}")

        # Prefer explicit summary; otherwise derive from comment or original snippet
        _comment = str(item.get("comment") or "")
        _summary = str(item.get("summary") or "").strip()
        if not _summary:
            # Heuristic: first sentence or up to 80 chars
            head = _comment.strip().splitlines()[0] if _comment else ""
            if not head:
                head = original_text.strip()
            _summary = (head[:80] + ("…" if len(head) > 80 else "")) if head else ""

        priority_value = item.get("priority")
        priority = 0
        if isinstance(priority_value, int):
            priority = priority_value
        elif isinstance(priority_value, str):
            with suppress(ValueError):
                priority = int(priority_value)

        return ApiIssue(
            issue_id=str(item.get("issue_id") or ""),
            priority=priority,
            agent_name=str(item.get("agent_name") or "unknown"),
            summary=_summary,
            comment=_comment,
            original_text=original_text,
            span=span,
        )

    async def run_review_async(
        self,
        prd_text: str,
        *,
        on_event: Callable[[Event], None] | None = None,
    ) -> list[ApiIssue]:
        """
        PRDのレビューを非同期で実行する。呼び出し毎に独立した ADK セッションを生成・破棄する。
        """
        try:
            model_name = os.getenv("ADK_MODEL") or "gemini-2.5-flash-lite"
            agent = create_parallel_review_agent(model=model_name)

            service = InMemorySessionService()  # type: ignore[no-untyped-call]
            app_name = "hibikasu_review_api"
            user_id = f"api_user_{uuid4()}"
            session_id = f"sess_{uuid4()}"

            await service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
            runner = Runner(agent=agent, app_name=app_name, session_service=service)

            content = genai_types.Content(role="user", parts=[genai_types.Part(text=str(prd_text))])

            _t0 = time.perf_counter()
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                # Drain events; optionally hand them to caller for progress updates
                if on_event:
                    try:
                        on_event(event)
                    except Exception as cb_err:
                        logger.warning("on_event callback failed", exc_info=cb_err)
            _elapsed_ms = int((time.perf_counter() - _t0) * 1000)

            sess = await service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
            state = getattr(sess, "state", {}) if sess else {}
            final_review_issues = state.get("final_review_issues")
            if not final_review_issues or not isinstance(final_review_issues, dict):
                logger.error("No final_review_issues in state")
                return []
            final_issues: list[dict[str, object]] = final_review_issues.get("final_issues", [])

            # Expect a typed FinalIssuesResponse object and access directly

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
                    api_issue = self._create_api_issue(item, prd_text)
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
