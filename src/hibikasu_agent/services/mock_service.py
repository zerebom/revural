from __future__ import annotations

import time
import uuid
from typing import Any, cast

from hibikasu_agent.api.schemas import Issue, IssueSpan
from hibikasu_agent.services.base import ReviewServiceBase


class MockService(ReviewServiceBase):
    """Simple in-memory mock review service for local/dev use."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    @property
    def reviews_in_memory(self) -> dict[str, dict[str, Any]]:
        return self._store

    def new_review_session(self, prd_text: str, panel_type: str | None = None) -> str:
        review_id = str(uuid.uuid4())
        self._store[review_id] = {
            "created_at": time.time(),
            "status": "processing",
            "issues": None,
            "prd_text": prd_text,
            "panel_type": panel_type,
            "polls": 0,
        }
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

    def get_review_session(self, review_id: str) -> dict[str, Any]:
        data = self._store.get(review_id)
        if not data:
            return {"status": "not_found", "issues": None}

        now = time.time()
        data["polls"] = int(data.get("polls", 0)) + 1
        if (now - data["created_at"]) < 2.0 and data["polls"] <= 1:
            return {"status": "processing", "issues": None}

        if data.get("issues") is None:
            issues = self._dummy_issues(str(data.get("prd_text", "")))
            prd_text = str(data.get("prd_text", ""))
            for iss in issues:
                if iss.span is not None:
                    continue
                snippet = (iss.original_text or "").strip()
                if not snippet:
                    continue
                pos = prd_text.find(snippet)
                if pos >= 0:
                    iss.span = IssueSpan(start_index=pos, end_index=pos + len(snippet))
            data["issues"] = issues
            data["status"] = "completed"

        return {"status": cast(str, data.get("status")), "issues": data.get("issues")}

    def find_issue(self, review_id: str, issue_id: str) -> Issue | None:
        session = self._store.get(review_id)
        if not session or not session.get("issues"):
            return None
        issues: list[Issue] = cast("list[Issue]", session["issues"])  # pydantic models at runtime
        for issue in issues:
            if issue.issue_id == issue_id:
                return issue
        return None
