from __future__ import annotations

from hibikasu_agent.api.schemas.reviews import IssueSpan
from hibikasu_agent.utils.span_calculator import calculate_span, find_simple_span, normalize_text


def test_normalize_text_removes_whitespace() -> None:
    assert normalize_text(" a b\tc\n") == "abc"


def test_find_simple_span_returns_span_when_found() -> None:
    span = find_simple_span("abcdef", "cd")
    assert span == IssueSpan(start_index=2, end_index=4)


def test_find_simple_span_returns_none_when_missing() -> None:
    assert find_simple_span("abcdef", "gh") is None


def test_calculate_span_handles_normalized_text() -> None:
    prd = "Line 1\nLine 2 with  spaces"
    original = "Line2withspaces"
    span = calculate_span(prd, original)
    assert span is not None
    assert prd[span.start_index : span.end_index].replace(" ", "") == "Line2withspaces"


def test_calculate_span_handles_nfkc_and_case() -> None:
    prd = "ユーザー数は10万です"
    original = "ﾕｰｻﾞｰ数は１０万です"
    span = calculate_span(prd, original)
    assert span is not None
    assert prd[span.start_index : span.end_index] == "ユーザー数は10万です"


def test_calculate_span_handles_minor_variations_via_fuzzy_match() -> None:
    prd = "ユーザーはサインアップし、データを保存します。"
    original = "ユーザーはサインアップしてデータを保存します"
    span = calculate_span(prd, original)
    assert span is not None
    assert prd[span.start_index : span.end_index].startswith("ユーザーはサインアップ")


def test_calculate_span_falls_back_to_simple_search() -> None:
    prd = "abc xyz"
    original = "xyz"
    span = calculate_span(prd, original)
    assert span == IssueSpan(start_index=4, end_index=7)


def test_calculate_span_returns_none_for_missing_text() -> None:
    assert calculate_span("abc", "") is None
    assert calculate_span("abc", "xyz") is None


def test_calculate_span_returns_none_when_similarity_low() -> None:
    prd = "プロダクトの目的は売上拡大です。"
    original = "全く関係のない文章です"
    assert calculate_span(prd, original) is None
