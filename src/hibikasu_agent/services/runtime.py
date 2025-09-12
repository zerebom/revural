from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from typing import Any, cast

from hibikasu_agent.api.schemas import Issue, IssueSpan
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)

# In-memory store for review sessions (API-compatible shape)
reviews_in_memory: dict[str, dict[str, Any]] = {}

# Pluggable review implementation for testing/injection.
# Signature: (prd_text: str) -> list[Issue]
_review_impl_holder: list[Callable[[str], list[Issue]] | None] = [None]


def set_review_impl(func: Callable[[str], list[Issue]] | None) -> None:
    _review_impl_holder[0] = func


def has_review_impl() -> bool:
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
    logger.info(
        "new_review_session created",
        extra={
            "review_id": review_id,
            "panel_type": panel_type or "",
            "prd_len": len(prd_text or ""),
        },
    )
    return review_id


def _default_review_impl(prd_text: str) -> list[Issue]:
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

    data["polls"] = int(data.get("polls", 0)) + 1
    logger.debug(
        "poll review_session",
        extra={"review_id": review_id, "polls": data["polls"], "status": data.get("status")},
    )
    if data["polls"] <= 1:
        logger.info(
            "first poll -> processing",
            extra={"review_id": review_id},
        )
        return {"status": "processing", "issues": None}

    status = str(data.get("status", "processing"))
    issues = data.get("issues")
    if status == "completed":
        logger.info(
            "poll -> completed",
            extra={"review_id": review_id, "issues_count": len(issues or []) if isinstance(issues, list) else 0},
        )
    return {"status": status, "issues": issues}


def find_issue(review_id: str, issue_id: str) -> Issue | None:
    session = reviews_in_memory.get(review_id)
    if not session or not session.get("issues"):
        return None
    issues: list[Issue] = cast("list[Issue]", session["issues"])  # populated by compute
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
        t0 = time.perf_counter()
        logger.info(
            "kickoff_compute starting",
            extra={
                "review_id": review_id,
                "prd_len": len(str(data.get("prd_text", ""))),
            },
        )
        impl = _review_impl_holder[0] or _default_review_impl
        prd_text = str(data.get("prd_text", ""))
        issues = impl(prd_text)
        # Enrich issues with span if not provided
        spans_added = 0
        try:
            for iss in issues or []:
                if getattr(iss, "span", None) is not None:
                    continue
                # naive first occurrence match
                snippet = (iss.original_text or "").strip()
                if not snippet:
                    continue
                start = prd_text.find(snippet)
                if start >= 0:
                    end = start + len(snippet)
                    try:
                        iss.span = IssueSpan(start_index=start, end_index=end)
                        spans_added += 1
                    except Exception:  # nosec B110
                        # ignore span assignment errors to avoid failing the whole review
                        pass
        except Exception:  # nosec B110
            # Best-effort enrichment; do not impact completion
            pass

        data["issues"] = issues
        data["status"] = "completed"
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        logger.info(
            "kickoff_compute completed",
            extra={
                "review_id": review_id,
                "issues_count": len(issues) if issues else 0,
                "spans_added": spans_added,
                "elapsed_ms": elapsed_ms,
            },
        )
    except Exception as _err:
        data["status"] = "failed"
        data["error"] = str(_err)
        logger.error("kickoff_compute failed", extra={"review_id": review_id, "error": str(_err)})
