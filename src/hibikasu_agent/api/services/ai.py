from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from typing import Any, cast

from hibikasu_agent.api.schemas import Issue

# In-memory store for AI mode as well (compatible shape)
reviews_in_memory: dict[str, dict[str, Any]] = {}

# Pluggable review implementation for testing/injection.
# Signature: (prd_text: str) -> list[Issue]
_review_impl_holder: list[Callable[[str], list[Issue]] | None] = [None]


def set_review_impl(func: Callable[[str], list[Issue]] | None) -> None:
    _review_impl_holder[0] = func


def has_review_impl() -> bool:
    """Return True if a custom review implementation has been registered.

    Used by app startup to avoid overriding test-injected or user-provided impls.
    """
    return _review_impl_holder[0] is not None


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

    # simple state machine:
    # - first poll: always report processing for deterministic UX
    # - compute is performed by BackgroundTasks via kickoff_compute()
    # - subsequent polls: return current state (completed when issues are ready)
    data["polls"] = int(data.get("polls", 0)) + 1
    if data["polls"] <= 1:
        return {"status": "processing", "issues": None}

    return {"status": data.get("status", "processing"), "issues": data.get("issues")}


def find_issue(review_id: str, issue_id: str) -> Issue | None:
    session = reviews_in_memory.get(review_id)
    if not session or not session.get("issues"):
        return None
    issues: list[Issue] = cast("list[Issue]", session["issues"])  # populated by get_review_session
    for issue in issues:
        if issue.issue_id == issue_id:
            return issue
    return None


def kickoff_compute(review_id: str) -> None:
    """Compute issues for a review_id synchronously.

    Intended to be scheduled via FastAPI BackgroundTasks to avoid blocking requests.
    """
    data = reviews_in_memory.get(review_id)
    if not data:
        return
    if data.get("issues") is not None:
        return
    try:
        impl = _review_impl_holder[0] or _default_review_impl
        issues = impl(str(data.get("prd_text", "")))
        data["issues"] = issues
        data["status"] = "completed"
    except Exception as _err:
        # Mark as failed so polling doesn't spin forever; caller can inspect logs
        data["status"] = "failed"
        data["error"] = str(_err)


# Orchestrator-backed impl is injected from api.main lifespan only if needed.
