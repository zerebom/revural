"""Tests for review API with selected agent roles."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from hibikasu_agent.api.dependencies import get_review_service
from hibikasu_agent.api.main import app


@pytest.fixture
def mock_review_service_with_tracking():
    """Mock review service that tracks selected_agents."""
    mock_service = MagicMock()
    mock_service.new_review_session.return_value = "test-review-id"

    # Mock get_review_session to return selected agents info
    def get_review_session(review_id):
        if review_id == "test-review-id":
            return {
                "status": "processing",
                "issues": None,
                "prd_text": "Test PRD",
                "expected_agents": ["engineer_specialist", "pm_specialist"],
                "completed_agents": [],
                "progress": 0.0,
                "phase": "starting",
            }
        return {"status": "not_found"}

    mock_service.get_review_session = get_review_session
    mock_service.kickoff_review = MagicMock()

    return mock_service


def test_start_review_with_selected_agents(mock_review_service_with_tracking):
    """POSTリクエストでselected_agent_rolesが渡されることを確認."""
    app.dependency_overrides[get_review_service] = lambda: mock_review_service_with_tracking

    with TestClient(app) as client:
        response = client.post("/reviews", json={"prd_text": "Test PRD", "selected_agent_roles": ["engineer", "pm"]})

        assert response.status_code == 200
        data = response.json()
        assert "review_id" in data

        # サービスが正しい引数で呼ばれたことを確認
        mock_review_service_with_tracking.new_review_session.assert_called_once()
        call_args = mock_review_service_with_tracking.new_review_session.call_args

        # 引数を確認 (位置引数またはキーワード引数)
        assert call_args[0][0] == "Test PRD"  # prd_text
        # selected_agentsがキーワード引数として渡されることを期待
        assert "selected_agents" in call_args[1]
        assert call_args[1]["selected_agents"] == ["engineer", "pm"]

    app.dependency_overrides = {}


def test_start_review_without_selected_agents(mock_review_service_with_tracking):
    """selected_agent_rolesなしでも後方互換性があることを確認."""
    # テストごとにモックをリセット
    mock_review_service_with_tracking.new_review_session.reset_mock()

    app.dependency_overrides[get_review_service] = lambda: mock_review_service_with_tracking

    with TestClient(app) as client:
        response = client.post("/reviews", json={"prd_text": "Test PRD"})

        assert response.status_code == 200
        data = response.json()
        assert "review_id" in data

        # selected_agentsはNoneで呼ばれるべき
        mock_review_service_with_tracking.new_review_session.assert_called_once()
        call_args = mock_review_service_with_tracking.new_review_session.call_args
        assert call_args[0][0] == "Test PRD"
        # selected_agentsが渡されているか確認（Noneのはず）
        if "selected_agents" in call_args[1]:
            assert call_args[1]["selected_agents"] is None

    app.dependency_overrides = {}
