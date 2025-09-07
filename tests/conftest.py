"""Pytest configuration and fixtures.

Ensure tests do not call external LLMs by injecting a deterministic
AI review implementation for the duration of each test. This keeps
tests fast, stable, and offline-friendly while exercising the API
flow and background task polling logic.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from hibikasu_agent.api import ai_services


@pytest.fixture(autouse=True)
def inject_fake_ai_impl() -> Generator[None, None, None]:
    """Auto-inject a fake AI review implementation for all tests.

    Returns a single deterministic issue using the API schema, so the
    service layer stores and returns predictable data.
    """

    def impl(prd_text: str):
        return [
            ai_services.Issue(
                issue_id="TST-1",
                priority=1,
                agent_name="AI-Orchestrator",
                comment="fake review",
                original_text=prd_text,
            )
        ]

    ai_services.set_review_impl(impl)
    try:
        yield
    finally:
        ai_services.set_review_impl(None)
