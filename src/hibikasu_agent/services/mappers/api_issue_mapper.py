"""Helpers for converting ADK output payloads into API models."""

from __future__ import annotations

from contextlib import suppress

from hibikasu_agent.api.schemas.reviews import Issue as ApiIssue
from hibikasu_agent.utils.span_calculator import calculate_span


def _coerce_priority(value: object | None) -> int:
    priority = 3
    if isinstance(value, int):
        priority = value
    elif isinstance(value, str):
        with suppress(ValueError):
            priority = int(value)

    if priority < 1 or priority > 3:
        return 3
    return priority


def map_api_issue(item: dict[str, object], prd_text: str) -> ApiIssue:
    """Transform a raw ADK issue dictionary into an API response model."""

    original_text = str(item.get("original_text") or "")
    span = calculate_span(prd_text, original_text)

    _comment = str(item.get("comment") or "")
    _summary = str(item.get("summary") or "").strip()

    priority = _coerce_priority(item.get("priority"))

    return ApiIssue(
        issue_id=str(item.get("issue_id") or ""),
        priority=priority,
        agent_name=str(item.get("agent_name") or "unknown"),
        summary=_summary,
        comment=_comment,
        original_text=original_text,
        span=span,
    )
