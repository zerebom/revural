"""Helpers for converting ADK output payloads into API models."""

from __future__ import annotations

from contextlib import suppress

from hibikasu_agent.api.schemas.reviews import Issue as ApiIssue
from hibikasu_agent.utils.span_calculator import calculate_span


def map_api_issue(item: dict[str, object], prd_text: str) -> ApiIssue:
    """Transform a raw ADK issue dictionary into an API response model."""

    original_text = str(item.get("original_text") or "")
    span = calculate_span(prd_text, original_text)

    _comment = str(item.get("comment") or "")
    _summary = str(item.get("summary") or "").strip()
    if not _summary:
        head = _comment.strip().splitlines()[0] if _comment else ""
        if not head:
            head = original_text.strip()
        _summary = (head[:80] + ("…" if len(head) > 80 else "")) if head else ""

    priority_value = item.get("priority")
    priority = 0
    if isinstance(priority_value, int):
        priority = priority_value
    elif isinstance(priority_value, str):
        with suppress(ValueError):
            priority = int(priority_value)

    return ApiIssue(
        issue_id=str(item.get("issue_id") or ""),
        priority=priority,
        agent_name=str(item.get("agent_name") or "unknown"),
        summary=_summary,
        comment=_comment,
        original_text=original_text,
        span=span,
    )
