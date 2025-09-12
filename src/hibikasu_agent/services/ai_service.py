from __future__ import annotations

from typing import Any, cast

from hibikasu_agent.api.schemas import Issue
from hibikasu_agent.services.base import AbstractReviewService
from hibikasu_agent.services.models import ReviewRuntimeSession
from hibikasu_agent.services.providers import adk
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


class AiService(AbstractReviewService):
    """AI-backed review service (self-contained).

    Manages its own in-memory session store and invokes the ADK pipeline
    via `providers.adk.run_review` to compute issues.
    """

    def __init__(self) -> None:
        self._reviews: dict[str, ReviewRuntimeSession] = {}

    @property
    def reviews_in_memory(self) -> dict[str, ReviewRuntimeSession]:
        return self._reviews

    def new_review_session(self, prd_text: str, panel_type: str | None = None) -> str:
        import time
        import uuid

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
        from hibikasu_agent.api.schemas import IssueSpan

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

    def kickoff_compute(self, review_id: str) -> None:
        sess = self._reviews.get(review_id)
        if not sess or sess.issues is not None:
            return
        try:
            issues = adk.run_review(sess.prd_text)
        except Exception as err:  # nosec B110
            sess.status = "failed"
            sess.error = str(err)
            logger.error("ai review failed", extra={"review_id": review_id, "error": str(err)})
            return
        self._enrich_issue_spans(sess.prd_text, issues)
        sess.issues = issues
        sess.status = "completed"

    async def start_review_process(self, prd_text: str, panel_type: str | None = None) -> str:
        review_id = self.new_review_session(prd_text, panel_type)
        # Start compute on a background thread to avoid blocking
        try:
            import threading

            threading.Thread(target=self.kickoff_compute, args=(review_id,), daemon=True).start()
        except Exception:  # nosec B110
            # Fallback to synchronous compute
            self.kickoff_compute(review_id)
        return review_id
