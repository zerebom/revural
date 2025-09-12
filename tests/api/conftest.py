from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from hibikasu_agent.api.dependencies import get_service
from hibikasu_agent.api.main import app
from hibikasu_agent.services.mock_service import MockService


@pytest.fixture
def mock_service_override():
    """Override DI to always use MockService for API tests."""

    def override_get_service():
        return MockService()

    app.dependency_overrides[get_service] = override_get_service
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_service, None)


@pytest.fixture
def client(mock_service_override):
    """TestClient with MockService injected via dependency_overrides."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def client_ai_mode():
    """TestClient without DI override (env-driven service selection)."""
    with TestClient(app) as c:
        yield c
