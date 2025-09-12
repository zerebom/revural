"""Pytest configuration and fixtures.

Ensure tests do not call external LLMs by injecting a deterministic
AI review implementation for the duration of each test. This keeps
tests fast, stable, and offline-friendly while exercising the API
flow and background task polling logic.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from hibikasu_agent.api.schemas import Issue
from hibikasu_agent.services.providers import adk


@pytest.fixture(autouse=True)
def inject_fake_ai_impl(monkeypatch) -> Generator[None, None, None]:
    """Auto-inject a fake AI review implementation for all tests.

    Monkeypatch the ADK pipeline entry to return deterministic issues.
    """

    def impl(prd_text: str):
        return [
            Issue(
                issue_id="TST-1",
                priority=1,
                agent_name="AI-Orchestrator",
                comment="fake review",
                original_text=prd_text,
            )
        ]

    monkeypatch.setattr(adk, "run_review", impl, raising=False)
    try:
        yield
    finally:
        pass
