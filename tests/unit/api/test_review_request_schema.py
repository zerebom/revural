"""Tests for ReviewRequest schema with selected_agent_roles support."""

from hibikasu_agent.api.schemas.reviews import ReviewRequest


def test_review_request_with_selected_agents():
    """ReviewRequestがselected_agent_rolesを受け取れることを確認."""
    req = ReviewRequest(prd_text="テスト用のPRDテキスト", selected_agent_roles=["engineer", "pm"])
    assert req.prd_text == "テスト用のPRDテキスト"
    assert req.selected_agent_roles == ["engineer", "pm"]


def test_review_request_without_selected_agents():
    """後方互換性: selected_agent_rolesが未指定でも動作することを確認."""
    req = ReviewRequest(prd_text="テスト用のPRDテキスト")
    assert req.prd_text == "テスト用のPRDテキスト"
    assert req.selected_agent_roles is None


def test_review_request_with_empty_selected_agents():
    """空のselected_agent_rolesリストも受け取れることを確認."""
    req = ReviewRequest(prd_text="テスト用のPRDテキスト", selected_agent_roles=[])
    assert req.prd_text == "テスト用のPRDテキスト"
    assert req.selected_agent_roles == []
