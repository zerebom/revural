from __future__ import annotations

import asyncio
import time
import uuid
from collections import Counter
from typing import Any, cast

from hibikasu_agent.api.schemas import AgentCount, Issue, ReviewSummaryResponse, StatusCount, SummaryStatistics
from hibikasu_agent.services.base import AbstractReviewService
from hibikasu_agent.services.models import ReviewRuntimeSession
from hibikasu_agent.services.providers.adk import ADKService
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


class AiService(AbstractReviewService):
    """AI-backed review service.

    Manages in-memory review sessions and uses an ADKService provider
    to compute review issues asynchronously.
    """

    def __init__(self, adk_service: ADKService) -> None:
        self._reviews: dict[str, ReviewRuntimeSession] = {}
        self.adk_service = adk_service

    @property
    def reviews_in_memory(self) -> dict[str, ReviewRuntimeSession]:
        return self._reviews

    def new_review_session(self, prd_text: str, panel_type: str | None = None) -> str:
        review_id = str(uuid.uuid4())
        self._reviews[review_id] = ReviewRuntimeSession(
            created_at=time.time(),
            status="processing",
            issues=None,
            prd_text=prd_text,
            panel_type=panel_type,
        )
        return review_id

    def get_review_session(self, review_id: str) -> dict[str, Any]:
        sess = self._reviews.get(review_id)
        if not sess:
            return {"status": "not_found", "issues": None}
        return {"status": sess.status, "issues": sess.issues, "prd_text": sess.prd_text}

    def find_issue(self, review_id: str, issue_id: str) -> Issue | None:
        sess = self._reviews.get(review_id)
        if not sess or not sess.issues:
            return None
        issues: list[Issue] = cast("list[Issue]", sess.issues)
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
        sess = self._reviews.get(review_id)
        if not sess or sess.issues is not None:
            return
        try:
            issues = asyncio.run(self.adk_service.run_review_async(sess.prd_text))
        except Exception as err:  # nosec B110
            sess.status = "failed"
            sess.error = str(err)
            logger.error("ai review failed", extra={"review_id": review_id, "error": str(err)})
            return
        sess.issues = issues
        sess.status = "completed"

    def update_issue_status(self, review_id: str, issue_id: str, status: str) -> bool:
        sess = self._reviews.get(review_id)
        if not sess or not sess.issues:
            return False
        issues: list[Issue] = cast("list[Issue]", sess.issues)
        for iss in issues:
            if iss.issue_id == issue_id:
                # The API Issue model has an optional status field
                iss.status = status
                return True
        return False

    def get_review_summary(self, review_id: str) -> dict[str, Any]:
        sess = self._reviews.get(review_id)
        if not sess:
            empty = SummaryStatistics()
            return ReviewSummaryResponse(status="not_found", statistics=empty, issues=[]).model_dump()

        issues: list[Issue] = []
        if sess.issues:
            issues = cast("list[Issue]", sess.issues)

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
