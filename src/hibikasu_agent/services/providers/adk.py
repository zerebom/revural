from __future__ import annotations

import os
import re
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

    def _normalize_text(self, text: str) -> str:
        """テキストから空白文字（スペース、タブ、改行など）をすべて除去する"""
        return re.sub(r"\s+", "", text)

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
            start_index_simple = prd_text.find(original_text)
            if start_index_simple != -1:
                return IssueSpan(
                    start_index=start_index_simple,
                    end_index=start_index_simple + len(original_text),
                )
            return None

        # 正規化された開始位置(start_index_normalized)を、元の文字列インデックスへマップ
        # アルゴリズム: 元テキストを先頭から走査し、非空白文字を start_index_normalized 個スキップした
        # 次の非空白文字の位置を開始インデックスとする。
        actual_start_index = -1
        non_space_seen = 0
        for i, ch in enumerate(prd_text):
            if not ch.isspace():
                if non_space_seen == start_index_normalized:
                    actual_start_index = i
                    break
                non_space_seen += 1

        if actual_start_index == -1:
            # start_index_normalized が 0 の場合など、最初の非空白が開始
            if start_index_normalized == 0:
                # 最初の非空白を探す
                for i, ch in enumerate(prd_text):
                    if not ch.isspace():
                        actual_start_index = i
                        break
                if actual_start_index == -1:
                    actual_start_index = 0
            else:
                return None

        # 終端は、開始から "original_normalized" の長さ分の非空白文字をカバーする位置まで進める
        target_len = len(original_normalized)
        covered = 0
        actual_end_index = actual_start_index
        for j in range(actual_start_index, len(prd_text)):
            c = prd_text[j]
            if not c.isspace():
                covered += 1
                if covered >= target_len:
                    actual_end_index = j + 1  # 半開区間のため +1
                    break
        else:
            # 末尾までに満たない場合は末尾を終端にする
            actual_end_index = len(prd_text)

        return IssueSpan(start_index=actual_start_index, end_index=actual_end_index)

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
            final_review_issues = state.get("final_review_issues")
            if not final_review_issues or not isinstance(final_review_issues, dict):
                logger.error("No final_review_issues in state")
                return []
            final_issues: list[dict] = final_review_issues.get("final_issues", [])

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
                    api_issues.append(
                        ApiIssue(
                            issue_id=str(item.get("issue_id") or ""),
                            priority=int(item.get("priority") or 0),
                            agent_name=str(item.get("agent_name") or "unknown"),
                            summary=_summary,
                            comment=str(item.get("comment") or ""),
                            original_text=original_text,
                            span=span,
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
            return [
                ApiIssue(
                    issue_id="AI-ERROR",
                    priority=1,
                    agent_name="AI-Orchestrator",
                    summary="ADK実行エラー",
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
