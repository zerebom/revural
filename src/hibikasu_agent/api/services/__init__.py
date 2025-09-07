from __future__ import annotations

from typing import cast

from hibikasu_agent.api.services.base import ReviewService
from hibikasu_agent.services import runtime as ai_service


def get_service() -> ReviewService:
    """Return the AI review service (AI-only)."""
    return cast(ReviewService, ai_service)
