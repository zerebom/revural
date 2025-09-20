"""Utilities for locating spans of original PRD text."""

from __future__ import annotations

import re

from hibikasu_agent.api.schemas.reviews import IssueSpan


def normalize_text(text: str) -> str:
    """Remove all whitespace characters to help align spans."""

    return re.sub(r"\s+", "", text)


def find_simple_span(prd_text: str, original_text: str) -> IssueSpan | None:
    """Fallback span detection using naive substring search."""

    start_index = prd_text.find(original_text)
    if start_index == -1:
        return None
    return IssueSpan(start_index=start_index, end_index=start_index + len(original_text))


def _find_normalized_start_index(prd_text: str, start_index_normalized: int) -> int:
    if start_index_normalized == 0:
        for i, ch in enumerate(prd_text):
            if not ch.isspace():
                return i
        return 0

    non_space_seen = 0
    for i, ch in enumerate(prd_text):
        if not ch.isspace():
            if non_space_seen == start_index_normalized:
                return i
            non_space_seen += 1
    return -1


def _find_end_index(prd_text: str, start_index: int, target_len: int) -> int:
    covered = 0
    for j in range(start_index, len(prd_text)):
        if not prd_text[j].isspace():
            covered += 1
            if covered >= target_len:
                return j + 1
    return len(prd_text)


def calculate_span(prd_text: str, original_text: str) -> IssueSpan | None:
    """Calculate span of ``original_text`` within ``prd_text`` accounting for whitespace."""

    if not original_text:
        return None

    prd_normalized = normalize_text(prd_text)
    original_normalized = normalize_text(original_text)
    if not original_normalized:
        return None

    start_index_normalized = prd_normalized.find(original_normalized)
    if start_index_normalized == -1:
        return find_simple_span(prd_text, original_text)

    actual_start_index = _find_normalized_start_index(prd_text, start_index_normalized)
    if actual_start_index == -1:
        return None

    actual_end_index = _find_end_index(prd_text, actual_start_index, len(original_normalized))
    return IssueSpan(start_index=actual_start_index, end_index=actual_end_index)
