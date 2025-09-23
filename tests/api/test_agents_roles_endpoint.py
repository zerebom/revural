"""Tests for GET /agents/roles endpoint using t-wada style TDD."""

import pytest
from fastapi.testclient import TestClient
from hibikasu_agent.api.main import app


def test_get_agents_roles_returns_200():
    """GET /agents/roles should return 200 status."""
    with TestClient(app) as client:
        response = client.get("/agents/roles")
        assert response.status_code == 200


def test_get_agents_roles_returns_json_array():
    """GET /agents/roles should return a JSON array."""
    with TestClient(app) as client:
        response = client.get("/agents/roles")
        data = response.json()
        assert isinstance(data, list)


def test_get_agents_roles_contains_expected_roles():
    """GET /agents/roles should contain the 4 specialist roles."""
    with TestClient(app) as client:
        response = client.get("/agents/roles")
        data = response.json()

        roles = [item["role"] for item in data]
        expected_roles = ["engineer", "ux_designer", "qa_tester", "pm"]

        assert set(roles) == set(expected_roles)


def test_get_agents_roles_items_have_required_fields():
    """Each role item should have required fields and optional enrichment fields."""
    with TestClient(app) as client:
        response = client.get("/agents/roles")
        data = response.json()

        assert len(data) > 0

        for item in data:
            # Required fields
            assert "role" in item
            assert "display_name" in item
            assert "description" in item
            assert isinstance(item["role"], str)
            assert isinstance(item["display_name"], str)
            assert isinstance(item["description"], str)

            # Optional enrichment fields (currently None, ready for future)
            assert "role_label" in item
            assert "bio" in item
            assert "tags" in item
            assert "avatar_url" in item


def test_get_agents_roles_engineer_has_correct_data():
    """Engineer role should have correct display_name and description."""
    with TestClient(app) as client:
        response = client.get("/agents/roles")
        data = response.json()

        engineer = next((item for item in data if item["role"] == "engineer"), None)
        assert engineer is not None
        assert engineer["display_name"] == "Engineer Specialist"
        assert "エンジニア" in engineer["description"]


def test_get_agents_roles_engineer_has_enriched_fields():
    """Engineer role should have enriched UI fields from SpecialistDefinition."""
    with TestClient(app) as client:
        response = client.get("/agents/roles")
        data = response.json()

        engineer = next((item for item in data if item["role"] == "engineer"), None)
        assert engineer is not None

        # Check enriched fields
        assert engineer["role_label"] == "エンジニアAI"
        assert "スケーラブル" in engineer["bio"]
        assert "#API設計" in engineer["tags"]
        assert "#スケーラビリティ" in engineer["tags"]
        assert "#パフォーマンス" in engineer["tags"]
        assert engineer["avatar_url"] is None  # Not set yet


def test_all_agents_have_enriched_metadata():
    """All agents should have role_label, bio, and tags from SpecialistDefinition."""
    with TestClient(app) as client:
        response = client.get("/agents/roles")
        data = response.json()

        for agent in data:
            assert agent["role_label"] is not None
            assert agent["bio"] is not None
            assert agent["tags"] is not None
            assert len(agent["tags"]) > 0
            assert all(tag.startswith("#") for tag in agent["tags"])
