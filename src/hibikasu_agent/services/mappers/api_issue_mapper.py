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

    # Safety: Truncate original_text if it's too long (prevents huge responses)
    if len(original_text) > 200:
        # Remove excessive whitespace and newlines, then truncate
        cleaned_text = " ".join(original_text.split())
        original_text = cleaned_text[:200] + "..." if len(cleaned_text) > 200 else cleaned_text

    span = calculate_span(prd_text, original_text)

    _comment = str(item.get("comment") or "")
    _summary = str(item.get("summary") or "").strip()

    # If no summary provided, derive from comment or original_text
    if not _summary:
        if _comment:
            # Extract first sentence from comment
            first_sentence = _comment.split(".")[0]
            _summary = first_sentence.strip()
        else:
            # Fallback to original_text
            _summary = original_text

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
