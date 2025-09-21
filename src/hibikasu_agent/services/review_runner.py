"""Wrapper around ADK provider to execute reviews."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from hibikasu_agent.api.schemas.reviews import Issue
from hibikasu_agent.services.providers.adk import ADKService


class AdkReviewRunner:
    """Coordinates execution of the ADK review workflow."""

    def __init__(self, adk_service: ADKService) -> None:
        self._adk_service = adk_service

    async def run_async(
        self,
        prd_text: str,
        *,
        on_event: Callable[[Any], None] | None = None,
        selected_agents: list[str] | None = None,
    ) -> list[Issue]:
        """Execute the review asynchronously and yield issues returned by the provider."""

        return await self._adk_service.run_review_async(prd_text, on_event=on_event, selected_agents=selected_agents)

    def run_blocking(
        self,
        prd_text: str,
        *,
        on_event: Callable[[Any], None] | None = None,
        selected_agents: list[str] | None = None,
    ) -> list[Issue]:
        """Execute the review using a temporary event loop and return the result."""

        return asyncio.run(self.run_async(prd_text, on_event=on_event, selected_agents=selected_agents))
