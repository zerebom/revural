from __future__ import annotations

import time
import uuid
from collections import Counter
from typing import Any

from google.adk.events.event import Event as ADKEvent

from hibikasu_agent.api.schemas.reviews import AgentCount, Issue, ReviewSummaryResponse, StatusCount, SummaryStatistics
from hibikasu_agent.constants.agents import (
    AGENT_DISPLAY_NAMES,
    SPECIALIST_AGENT_KEYS,
    STATE_KEY_TO_AGENT_KEY,
)
from hibikasu_agent.services.base import AbstractReviewService
from hibikasu_agent.services.models import ReviewRuntimeSession
from hibikasu_agent.services.providers.adk import ADKService
from hibikasu_agent.services.review_runner import AdkReviewRunner
from hibikasu_agent.services.review_store import ReviewSessionStore
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


def _agent_display_name(agent_name: str) -> str:
    if not agent_name:
        return ""
    pretty = AGENT_DISPLAY_NAMES.get(agent_name)
    if pretty:
        return pretty
    return agent_name.replace("_", " ").title()


def _extract_error_message(err: Exception) -> str:
    """Return a concise, user-facing error description."""

    visited: set[int] = set()
    current: BaseException | None = err
    while current and id(current) not in visited:
        visited.add(id(current))
        if hasattr(current, "errors") and callable(current.errors):
            try:
                errors = current.errors()
            except Exception:
                errors = []
            if errors:
                first = errors[0]
                loc = first.get("loc")
                msg = first.get("msg") or str(current)
                if loc:
                    loc_text = ".".join(str(part) for part in loc)
                    return f"{loc_text}: {msg}"
                return str(msg)
        current = current.__cause__ or current.__context__

    text = str(err).strip()
    if text:
        return text.splitlines()[0][:200]
    return err.__class__.__name__


class AiService(AbstractReviewService):
    """AI-backed review service.

    Manages in-memory review sessions and uses an ADKService provider
    to compute review issues asynchronously.
    """

    def __init__(
        self,
        adk_service: ADKService,
        *,
        review_store: ReviewSessionStore | None = None,
        review_runner: AdkReviewRunner | None = None,
    ) -> None:
        self.adk_service = adk_service
        self._store = review_store or ReviewSessionStore()
        self._review_runner = review_runner or AdkReviewRunner(adk_service)

    @property
    def reviews_in_memory(self) -> dict[str, ReviewRuntimeSession]:
        return dict(self._store.as_dict())

    def new_review_session(
        self, prd_text: str, panel_type: str | None = None, *, selected_agents: list[str] | None = None
    ) -> str:
        """Create a new review session with optional agent selection.

        Args:
            prd_text: The PRD text to review
            panel_type: Optional panel type for categorization
            selected_agents: Optional list of agent roles to use (e.g., ["engineer", "pm"])
        """
        review_id = str(uuid.uuid4())

        # Get expected agent keys based on selection
        if selected_agents is not None:
            expected_agents = self.adk_service.get_selected_agent_keys(selected_agents)
        else:
            raw_expected = getattr(self.adk_service, "default_review_agents", SPECIALIST_AGENT_KEYS)
            if callable(raw_expected):  # defensive for stubs returning a factory
                raw_expected = raw_expected()
            expected_agents = list(raw_expected or SPECIALIST_AGENT_KEYS)

        phase_message = None
        if expected_agents:
            phase_message = f"{len(expected_agents)}名の専門家がレビューを開始しました"

        session = ReviewRuntimeSession(
            created_at=time.time(),
            status="processing",
            issues=None,
            prd_text=prd_text,
            panel_type=panel_type,
            expected_agents=expected_agents,
            completed_agents=[],
            progress=0.0,
            phase="processing",
            phase_message=phase_message,
            selected_agent_roles=selected_agents,  # Store original selection
        )
        self._store.create(review_id, session)
        return review_id

    def get_review_session(self, review_id: str) -> dict[str, Any]:
        sess = self._store.get(review_id)
        if not sess:
            return {"status": "not_found", "issues": None}
        return {
            "status": sess.status,
            "issues": sess.issues,
            "prd_text": sess.prd_text,
            "progress": sess.progress,
            "phase": sess.phase,
            "phase_message": sess.phase_message,
            "eta_seconds": sess.eta_seconds,
            "expected_agents": sess.expected_agents,
            "completed_agents": sess.completed_agents,
        }

    def find_issue(self, review_id: str, issue_id: str) -> Issue | None:
        sess = self._store.get(review_id)
        if not sess or not sess.issues:
            return None
        issues = sess.issues
        for iss in issues:
            if iss.issue_id == issue_id:
                return iss
        return None

    async def answer_dialog(self, review_id: str, issue_id: str, question_text: str) -> str:
        issue = self.find_issue(review_id, issue_id)
        if not issue:
            return "該当する論点が見つかりませんでした。"
        return await self.adk_service.answer_dialog_async(issue, question_text)

    def kickoff_review(self, review_id: str) -> None:
        """同期メソッド。BackgroundTasks から呼ばれて非同期レビューを実行する。"""
        sess = self._store.get(review_id)
        if not sess or sess.issues is not None:
            return

        def _on_event(event: Any) -> None:
            try:
                self._handle_adk_event(sess, event)
            except Exception:  # nosec B110
                logger.debug("failed to handle ADK event", exc_info=True)

        try:
            issues = self._review_runner.run_blocking(
                sess.prd_text, on_event=_on_event, selected_agents=sess.selected_agent_roles
            )
        except Exception as err:  # nosec B110
            message = _extract_error_message(err)
            sess.status = "failed"
            sess.error = str(err)
            sess.phase = "failed"
            sess.phase_message = f"レビューの実行中にエラーが発生しました: {message}"
            logger.error(
                "ai review failed",
                extra={"review_id": review_id, "error": str(err)},
                exc_info=True,
            )
            return
        sess.issues = issues
        sess.status = "completed"
        sess.phase = "completed"
        sess.progress = 1.0
        if sess.expected_agents:
            remaining = [agent for agent in sess.expected_agents if agent not in sess.completed_agents]
            if remaining:
                sess.completed_agents.extend(remaining)
        sess.phase_message = "レビューが完了しました"

    def update_issue_status(self, review_id: str, issue_id: str, status: str) -> bool:
        sess = self._store.get(review_id)
        if not sess or not sess.issues:
            return False
        issues = sess.issues
        for iss in issues:
            if iss.issue_id == issue_id:
                # The API Issue model has an optional status field
                iss.status = status
                return True
        return False

    def get_review_summary(self, review_id: str) -> dict[str, Any]:
        sess = self._store.get(review_id)
        if not sess:
            empty = SummaryStatistics()
            return ReviewSummaryResponse(status="not_found", statistics=empty, issues=[]).model_dump()

        issues: list[Issue] = []
        if sess.issues:
            issues = sess.issues

        total = len(issues)
        status_counter: Counter[str] = Counter()
        agent_counter: Counter[str] = Counter()

        for issue in issues:
            status = (issue.status or "pending").strip().lower() or "pending"
            status_counter[status] += 1
            agent_counter[issue.agent_name or "Unknown"] += 1

        # normalize status order and labels
        label_map = {
            "done": "対応済み",
            "pending": "未対応",
            "later": "あとで",
        }
        preferred_order = ["done", "pending", "later"]

        status_counts: list[StatusCount] = []
        for key in preferred_order:
            if key in status_counter:
                status_counts.append(
                    StatusCount(key=key, label=label_map.get(key, key.title()), count=status_counter[key])
                )
        for key, count in status_counter.items():
            if key not in {"done", "pending", "later"}:
                status_counts.append(StatusCount(key=key, label=label_map.get(key, key.title()), count=count))

        agent_counts = [AgentCount(agent_name=name, count=count) for name, count in agent_counter.items()]
        agent_counts.sort(key=lambda x: (-x.count, x.agent_name.lower()))

        statistics = SummaryStatistics(total_issues=total, status_counts=status_counts, agent_counts=agent_counts)
        response = ReviewSummaryResponse(status=sess.status, statistics=statistics, issues=issues)
        return response.model_dump()

    # ------------------------------------------------------------------
    # Internal helpers

    def _handle_adk_event(self, sess: ReviewRuntimeSession, event: Any) -> None:
        """Update runtime session based on ADK event callbacks."""

        if not isinstance(event, ADKEvent):
            return

        expected = sess.expected_agents
        if not expected:
            return

        matched_agents: list[str] = []
        state_delta = getattr(getattr(event, "actions", None), "state_delta", None)
        if isinstance(state_delta, dict):
            # レスポンスサイズをログ出力
            for key, value in state_delta.items():
                if value:
                    value_str = str(value)
                    logger.info(f"ADK state delta - key: {key}, size: {len(value_str)} chars")

                    # 巨大なレスポンスを警告
                    if len(value_str) > 50000:
                        logger.warning(f"⚠️ HUGE RESPONSE DETECTED! key: {key}, size: {len(value_str)} chars")
                        logger.info(f"Response preview (first 1000 chars): {value_str[:1000]}")

            for state_key in state_delta:
                agent_key = STATE_KEY_TO_AGENT_KEY.get(state_key)
                if agent_key and agent_key in expected:
                    matched_agents.append(agent_key)

        if not matched_agents:
            logger.debug(
                "adk event did not include known state updates",
                extra={
                    "expected": expected,
                    "state_delta_keys": list(state_delta.keys()) if isinstance(state_delta, dict) else None,
                },
            )
            return

        newly_completed = [agent for agent in matched_agents if agent not in sess.completed_agents]
        if newly_completed:
            sess.completed_agents.extend(newly_completed)
            self._recalculate_progress(sess, last_completed=newly_completed[-1])

    def _recalculate_progress(self, sess: ReviewRuntimeSession, *, last_completed: str | None = None) -> None:
        total = len(sess.expected_agents)
        completed = len(sess.completed_agents)
        if total <= 0:
            sess.progress = 0.0
            return
        sess.progress = min(1.0, completed / total)
        if sess.phase != "completed":
            if sess.progress < 1.0:
                sess.phase = "processing"
                if last_completed:
                    display = _agent_display_name(last_completed)
                    sess.phase_message = f"{display} のレビューが完了しました ({completed}/{total})"
                else:
                    sess.phase_message = f"専門家レビュー {completed}/{total} 件進行中"
            else:
                sess.phase = "aggregating"
                sess.phase_message = "専門家のレビューが完了しました。集約中です…"
