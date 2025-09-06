from __future__ import annotations

import time
import uuid
from typing import Any

from app.schemas import Issue

# In-memory store for Week1 mock implementation
reviews_in_memory: dict[str, dict[str, Any]] = {}


def new_review_session(prd_text: str, panel_type: str | None = None) -> str:
    review_id = str(uuid.uuid4())
    reviews_in_memory[review_id] = {
        "created_at": time.time(),
        "status": "processing",
        "issues": None,
        "prd_text": prd_text,
        "panel_type": panel_type,
        # simple counter for demo if needed
        "polls": 0,
    }
    return review_id


def _dummy_issues() -> list[Issue]:
    # Deterministic sample issues matching architecture.md 10.1 fields
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


def get_review_session(review_id: str) -> dict[str, Any]:
    data = reviews_in_memory.get(review_id)
    if not data:
        return {"status": "not_found", "issues": None}

    # Simulate processing for first ~2 seconds or first poll
    now = time.time()
    data["polls"] = int(data.get("polls", 0)) + 1
    if (now - data["created_at"]) < 2.0 and data["polls"] <= 1:
        return {"status": "processing", "issues": None}

    # Mark as completed and attach dummy issues once
    if data.get("issues") is None:
        data["issues"] = _dummy_issues()
        data["status"] = "completed"

    return {"status": data["status"], "issues": data["issues"]}


def find_issue(review_id: str, issue_id: str) -> Issue | None:
    session = reviews_in_memory.get(review_id)
    if not session or not session.get("issues"):
        return None
    for issue in session["issues"]:
        if issue.issue_id == issue_id:
            return issue
    return None
