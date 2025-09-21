"""Tests for agent selection functionality."""

from __future__ import annotations

import pytest
from hibikasu_agent.agents.parallel_orchestrator.agent import create_parallel_review_agent
from hibikasu_agent.services.providers.adk import ADKService


def test_create_parallel_review_agent_with_selected_agents() -> None:
    """Test that create_parallel_review_agent accepts selected agents."""
    agent = create_parallel_review_agent(selected_agents=["engineer", "pm"])
    assert agent is not None
    assert agent.name == "ReviewPipelineWithTools"


def test_create_parallel_review_agent_with_invalid_agents() -> None:
    """Test that create_parallel_review_agent raises error for invalid agents."""
    with pytest.raises(ValueError, match="No valid agents found"):
        create_parallel_review_agent(selected_agents=["invalid_agent"])


def test_create_parallel_review_agent_with_all_agents() -> None:
    """Test that create_parallel_review_agent works with all available agents."""
    agent = create_parallel_review_agent(selected_agents=["engineer", "ux_designer", "qa_tester", "pm"])
    assert agent is not None


def test_create_parallel_review_agent_with_none_agents() -> None:
    """Test that create_parallel_review_agent works with None (default all agents)."""
    agent = create_parallel_review_agent(selected_agents=None)
    assert agent is not None


def test_adk_service_available_agent_roles() -> None:
    """Test that ADKService returns available agent roles."""
    service = ADKService()
    roles = service.available_agent_roles

    expected_roles = ["engineer", "ux_designer", "qa_tester", "pm"]
    assert set(roles) == set(expected_roles)


def test_adk_service_get_selected_agent_keys() -> None:
    """Test agent role to key conversion."""
    service = ADKService()

    # Test with valid roles
    keys = service.get_selected_agent_keys(["engineer", "pm"])
    assert "engineer_specialist" in keys
    assert "pm_specialist" in keys
    assert len(keys) == 2

    # Test with None (should return defaults)
    default_keys = service.get_selected_agent_keys(None)
    assert len(default_keys) == 4

    # Test with invalid roles (should return defaults)
    invalid_keys = service.get_selected_agent_keys(["invalid_role"])
    assert invalid_keys == service.default_review_agents
