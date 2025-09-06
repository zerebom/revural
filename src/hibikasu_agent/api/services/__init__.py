from __future__ import annotations

from typing import TYPE_CHECKING

from hibikasu_agent.api import ai_services as ai_service
from hibikasu_agent.api import config
from hibikasu_agent.api.services import mock as mock_service

if TYPE_CHECKING:  # typing-only
    from hibikasu_agent.api.services.base import ReviewService


def get_service() -> ReviewService:
    """Select mock or ai service based on settings each call."""
    return ai_service if config.is_ai_mode() else mock_service
