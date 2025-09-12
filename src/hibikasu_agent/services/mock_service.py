from __future__ import annotations

import time
import uuid
from typing import cast

from hibikasu_agent.api.schemas import Issue, IssueSpan
from hibikasu_agent.services.base import AbstractReviewService
from hibikasu_agent.services.models import ReviewRuntimeSession


class MockService(AbstractReviewService):
    """Simple in-memory mock review service for local/dev use."""

    def __init__(self) -> None:
        self._store: dict[str, ReviewRuntimeSession] = {}

    @property
    def reviews_in_memory(self) -> dict[str, ReviewRuntimeSession]:
        return self._store

    def new_review_session(self, prd_text: str, panel_type: str | None = None) -> str:
        review_id = str(uuid.uuid4())
        self._store[review_id] = ReviewRuntimeSession(
            created_at=time.time(),
            status="processing",
            issues=None,
            prd_text=prd_text,
            panel_type=panel_type,
        )
        return review_id

    def _dummy_issues(self, prd_text: str) -> list[Issue]:
        return [
            Issue(
                issue_id="ISSUE-001",
                priority=1,
                agent_name="エンジニアAI",
                comment=(
                    "カスタマイズ項目の保存ロジックにN+1問題が発生するリスクがあります。"
                    "大量の項目を一度に保存すると、パフォーマンスが著しく低下する可能性があります。"
                ),
                original_text="ユーザーはダッシュボードの表示項目を自由にカスタマイズし、その設定を保存できる。",
            ),
            Issue(
                issue_id="ISSUE-002",
                priority=2,
                agent_name="UXデザイナーAI",
                comment=(
                    "カスタマイズ項目が大量になった場合のUI表示が考慮されていません。"
                    "リストが長大になると、ユーザーが目的の項目を見つけるのが困難になります。"
                ),
                original_text="ユーザーはダッシュボードの表示項目を自由にカスタマイズできる。",
            ),
        ]

    def get_review_session(self, review_id: str) -> dict[str, object | None]:
        sess = self._store.get(review_id)
        if not sess:
            return {"status": "not_found", "issues": None}
        return {"status": sess.status, "issues": sess.issues}

    def find_issue(self, review_id: str, issue_id: str) -> Issue | None:
        session = self._store.get(review_id)
        if not session or not session.issues:
            return None
        issues: list[Issue] = cast("list[Issue]", session.issues)
        for issue in issues:
            if issue.issue_id == issue_id:
                return issue
        return None

    def kickoff_compute(self, review_id: str) -> None:
        sess = self._store.get(review_id)
        if not sess or sess.issues is not None:
            return
        prd_text = sess.prd_text
        issues = self._dummy_issues(prd_text)
        # Enrich spans
        for iss in issues:
            if iss.span is not None:
                continue
            snippet = (iss.original_text or "").strip()
            if not snippet:
                continue
            pos = prd_text.find(snippet)
            if pos >= 0:
                iss.span = IssueSpan(start_index=pos, end_index=pos + len(snippet))
        sess.issues = issues
        sess.status = "completed"

    async def start_review_process(self, prd_text: str, panel_type: str | None = None) -> str:
        """Create a session and kick off computation asynchronously."""
        review_id = self.new_review_session(prd_text, panel_type)
        # fire-and-forget thread to simulate background processing
        try:
            import threading

            threading.Thread(target=self.kickoff_compute, args=(review_id,), daemon=True).start()
        except Exception:
            # If background kickoff fails, compute synchronously as a fallback
            self.kickoff_compute(review_id)
        return review_id
