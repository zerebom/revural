"""Utilities for locating spans of original PRD text."""

from __future__ import annotations

import logging
import unicodedata
from difflib import SequenceMatcher

from hibikasu_agent.api.schemas.reviews import IssueSpan

_MIN_MATCH_RATIO = 0.5
logger = logging.getLogger(__name__)


def _build_normalized_view(text: str) -> tuple[str, list[int]]:
    """Return normalized text and mapping back to original indices."""

    chars: list[str] = []
    index_map: list[int] = []
    for idx, raw_ch in enumerate(text):
        normalized = unicodedata.normalize("NFKC", raw_ch)
        normalized = unicodedata.normalize("NFC", normalized).lower()
        for ch in normalized:
            if ch.isspace():
                continue
            if unicodedata.category(ch) == "Mn":
                if not chars:
                    continue
                combined = unicodedata.normalize("NFC", chars[-1] + ch)
                chars[-1] = combined[-1]
                continue
            chars.append(ch)
            index_map.append(idx)
    return ("".join(chars), index_map)


def normalize_text(text: str) -> str:
    """Return normalized text (no whitespace, width/case folded)."""

    normalized, _ = _build_normalized_view(text)
    return normalized


def find_simple_span(prd_text: str, original_text: str) -> IssueSpan | None:
    """Fallback span detection using naive substring search."""

    start_index = prd_text.find(original_text)
    if start_index == -1:
        return None
    return IssueSpan(start_index=start_index, end_index=start_index + len(original_text))


def _span_from_mapping(mapping: list[int], start: int, length: int) -> IssueSpan | None:
    if length <= 0:
        return None
    try:
        actual_start = mapping[start]
        actual_end_base = mapping[start + length - 1]
    except IndexError:
        return None
    return IssueSpan(start_index=actual_start, end_index=actual_end_base + 1)


def calculate_span(prd_text: str, original_text: str) -> IssueSpan | None:
    """Calculate span using normalization and fuzzy matching."""
    if not original_text:
        return None

    # Try simple span first
    simple_span = find_simple_span(prd_text, original_text)
    if simple_span is not None:
        return simple_span

    # Try normalized matching
    return _calculate_normalized_span(prd_text, original_text)


def _calculate_normalized_span(prd_text: str, original_text: str) -> IssueSpan | None:
    """Calculate span using normalization and fuzzy matching."""
    prd_normalized, mapping = _build_normalized_view(prd_text)
    original_normalized, _ = _build_normalized_view(original_text)

    if not original_normalized:
        logger.warning(
            "Span calculation failed: original_text became empty after normalization",
            extra={"original_text": original_text},
        )
        return None

    # Try direct substring search first
    direct_index = prd_normalized.find(original_normalized)
    if direct_index != -1:
        return _span_from_mapping(mapping, direct_index, len(original_normalized))

    # Fall back to fuzzy matching
    return _fuzzy_match_span(prd_normalized, original_normalized, original_text, mapping)


def _fuzzy_match_span(
    prd_normalized: str,
    original_normalized: str,
    original_text: str,
    mapping: list[int],
) -> IssueSpan | None:
    """Perform fuzzy matching and return span if match is good enough."""
    matcher = SequenceMatcher(None, prd_normalized, original_normalized, autojunk=False)
    match = matcher.find_longest_match(0, len(prd_normalized), 0, len(original_normalized))

    if match.size == 0:
        logger.warning(
            "Span calculation failed: no common subsequence found",
            extra={
                "original_text": original_text,
                "prd_normalized_len": len(prd_normalized),
                "original_normalized_len": len(original_normalized),
            },
        )
        return None

    coverage = match.size / len(original_normalized)
    if coverage < _MIN_MATCH_RATIO:
        logger.warning(
            "Span calculation failed: match coverage below threshold",
            extra={
                "original_text": original_text,
                "match_size": match.size,
                "original_normalized_len": len(original_normalized),
                "coverage": round(coverage, 2),
                "threshold": _MIN_MATCH_RATIO,
            },
        )
        return None

    span = _span_from_mapping(mapping, match.a, match.size)
    if span is None:
        logger.error(
            "Span calculation failed: could not map normalized span back to original indices",
            extra={
                "original_text": original_text,
                "match_a": match.a,
                "match_size": match.size,
                "mapping_len": len(mapping),
            },
        )

    return span
