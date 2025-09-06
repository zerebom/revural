from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:  # typing-only import
    from collections.abc import Callable

from hibikasu_agent.api.schemas import Issue

# In-memory store for AI mode as well (compatible shape)
reviews_in_memory: dict[str, dict[str, Any]] = {}

# Pluggable review implementation for testing/injection.
# Signature: (prd_text: str) -> list[Issue]
_review_impl_holder: list[Callable[[str], list[Issue]] | None] = [None]


def set_review_impl(func: Callable[[str], list[Issue]] | None) -> None:
    _review_impl_holder[0] = func


def new_review_session(prd_text: str, panel_type: str | None = None) -> str:
    review_id = str(uuid.uuid4())
    reviews_in_memory[review_id] = {
        "created_at": time.time(),
        "status": "processing",
        "issues": None,
        "prd_text": prd_text,
        "panel_type": panel_type,
        "polls": 0,
    }
    return review_id


def _default_review_impl(prd_text: str) -> list[Issue]:
    # Placeholder deterministic issues for AI mode until ADK integration lands
    return [
        Issue(
            issue_id="AI-001",
            priority=1,
            agent_name="AI-Orchestrator",
            comment="自動レビュー（暫定）: 仕様の曖昧さに注意してください。",
            original_text=prd_text[:80] or "(empty)",
        )
    ]


def get_review_session(review_id: str) -> dict[str, Any]:
    data = reviews_in_memory.get(review_id)
    if not data:
        return {"status": "not_found", "issues": None}

    # simple state machine: first poll stays processing, afterwards finalize
    data["polls"] = int(data.get("polls", 0)) + 1
    if data["issues"] is None and data["polls"] <= 1:
        return {"status": "processing", "issues": None}

    if data["issues"] is None:
        impl = _review_impl_holder[0] or _default_review_impl
        issues = impl(str(data.get("prd_text", "")))
        data["issues"] = issues
        data["status"] = "completed"

    return {"status": data["status"], "issues": data["issues"]}


def find_issue(review_id: str, issue_id: str) -> Issue | None:
    session = reviews_in_memory.get(review_id)
    if not session or not session.get("issues"):
        return None
    issues: list[Issue] = cast(list[Issue], session["issues"])  # populated by get_review_session
    for issue in issues:
        if issue.issue_id == issue_id:
            return issue
    return None
