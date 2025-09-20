"""Pytest configuration and fixtures.

Ensure tests do not call external LLMs by injecting a deterministic
AI review implementation for the duration of each test. This keeps
tests fast, stable, and offline-friendly while exercising the API
flow and background task polling logic.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from hibikasu_agent.api.schemas.reviews import Issue
from hibikasu_agent.services.providers.adk import ADKService


@pytest.fixture(autouse=True)
def inject_fake_ai_impl(monkeypatch) -> Generator[None, None, None]:
    """Auto-inject a fake AI review implementation for all tests.

    Monkeypatch the ADK pipeline entry to return deterministic issues.
    """

    async def impl_async(self, prd_text: str):  # type: ignore[no-untyped-def]
        return [
            Issue(
                issue_id="TST-1",
                priority=1,
                agent_name="AI-Orchestrator",
                comment="fake review",
                original_text=prd_text,
            )
        ]

    # Patch the provider's async review method (used in AiService)
    monkeypatch.setattr(ADKService, "run_review_async", impl_async, raising=False)
    try:
        yield
    finally:
        pass
