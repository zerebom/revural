"""Utilities for locating spans of original PRD text."""

from __future__ import annotations

import unicodedata
from difflib import SequenceMatcher

from hibikasu_agent.api.schemas.reviews import IssueSpan

_MIN_MATCH_RATIO = 0.5


def normalize_text(text: str) -> str:
    """Normalize text for comparisons (lowercase, width folding, remove whitespace)."""

    normalized, _ = _build_normalized_view(text)
    return normalized


def find_simple_span(prd_text: str, original_text: str) -> IssueSpan | None:
    """Direct substring search without normalization."""

    start_index = prd_text.find(original_text)
    if start_index == -1:
        return None
    return IssueSpan(start_index=start_index, end_index=start_index + len(original_text))


def _build_normalized_view(text: str) -> tuple[str, list[int]]:
    """Return normalized text and mapping to original indices."""

    chars: list[str] = []
    index_map: list[int] = []
    for idx, ch in enumerate(text):
        normalized = unicodedata.normalize("NFKC", ch)
        normalized = unicodedata.normalize("NFC", normalized).lower()
        for norm_ch in normalized:
            if norm_ch.isspace():
                continue
            if unicodedata.category(norm_ch) == "Mn":
                if not chars:
                    continue
                combined = unicodedata.normalize("NFC", chars[-1] + norm_ch)
                chars[-1] = combined[-1]
                continue
            chars.append(norm_ch)
            index_map.append(idx)
    return ("".join(chars), index_map)


def _span_from_mapping(prd_text: str, mapping: list[int], start: int, length: int) -> IssueSpan | None:
    if length <= 0:
        return None
    try:
        actual_start = mapping[start]
        actual_end_base = mapping[start + length - 1]
    except IndexError:
        return None
    return IssueSpan(start_index=actual_start, end_index=actual_end_base + 1)


def calculate_span(prd_text: str, original_text: str) -> IssueSpan | None:  # noqa: PLR0911
    """Calculate span of ``original_text`` within ``prd_text`` with fuzzy matching."""

    if not original_text:
        return None

    # Exact search first for perfect matches
    simple_span = find_simple_span(prd_text, original_text)
    if simple_span is not None:
        return simple_span

    prd_normalized, index_map = _build_normalized_view(prd_text)
    original_normalized, _ = _build_normalized_view(original_text)

    if not original_normalized:
        return None

    # Normalized direct search (ignoring whitespace/case/width)
    start_index_normalized = prd_normalized.find(original_normalized)
    if start_index_normalized != -1:
        return _span_from_mapping(prd_text, index_map, start_index_normalized, len(original_normalized))

    # Fuzzy matching for minor differences
    matcher = SequenceMatcher(None, prd_normalized, original_normalized, autojunk=False)
    match = matcher.find_longest_match(0, len(prd_normalized), 0, len(original_normalized))

    if match.size == 0:
        return None

    coverage = match.size / len(original_normalized)
    if coverage < _MIN_MATCH_RATIO:
        return None

    return _span_from_mapping(prd_text, index_map, match.a, match.size)
