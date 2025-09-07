from __future__ import annotations

from typing import cast

from hibikasu_agent.api.services import ai as ai_service
from hibikasu_agent.api.services.base import ReviewService


def get_service() -> ReviewService:
    """Return the AI review service (AI-only)."""
    return cast(ReviewService, ai_service)
