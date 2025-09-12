from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from hibikasu_agent.api.dependencies import get_service
from hibikasu_agent.api.main import app
from hibikasu_agent.services.ai_service import AiService
from hibikasu_agent.services.mock_service import MockService


@pytest.fixture(scope="session")
def shared_mock_service() -> MockService:
    """Create a single MockService instance shared across the test session."""
    return MockService()


@pytest.fixture(scope="session")
def shared_ai_service() -> AiService:
    """Create a single AiService instance shared across the test session."""
    return AiService()


@pytest.fixture
def client(shared_mock_service: MockService):
    """TestClient that always uses the same shared MockService instance."""
    app.dependency_overrides[get_service] = lambda: shared_mock_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_ai_mode(shared_ai_service: AiService):
    """TestClient that always uses the same shared AiService instance."""
    app.dependency_overrides[get_service] = lambda: shared_ai_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
