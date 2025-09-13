from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any, cast

from hibikasu_agent.api.schemas import Issue, IssueSpan
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
        return {"status": sess.status, "issues": sess.issues}

    def find_issue(self, review_id: str, issue_id: str) -> Issue | None:
        sess = self._reviews.get(review_id)
        if not sess or not sess.issues:
            return None
        issues: list[Issue] = cast("list[Issue]", sess.issues)
        for iss in issues:
            if iss.issue_id == issue_id:
                return iss
        return None

    def _enrich_issue_spans(self, prd_text: str, issues: list[Issue] | None) -> int:
        if not issues:
            return 0
        added = 0
        for iss in issues:
            try:
                if getattr(iss, "span", None) is not None:
                    continue
                snippet = (iss.original_text or "").strip()
                if not snippet:
                    continue
                start = prd_text.find(snippet)
                if start >= 0:
                    iss.span = IssueSpan(start_index=start, end_index=start + len(snippet))
                    added += 1
            except Exception:  # nosec B110
                continue
        return added

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
        self._enrich_issue_spans(sess.prd_text, issues)
        sess.issues = issues
        sess.status = "completed"
