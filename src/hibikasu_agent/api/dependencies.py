from __future__ import annotations

import os

from fastapi import Request

from hibikasu_agent.services.ai_service import AiService
from hibikasu_agent.services.base import AbstractReviewService
from hibikasu_agent.services.mock_service import MockService
from hibikasu_agent.services.providers.adk import ADKService


def _use_ai_mode() -> bool:
    mode = (os.getenv("HIBIKASU_API_MODE") or "").strip().lower()
    return mode == "ai"


def get_service(request: Request) -> AbstractReviewService:
    """Provide a review service instance based on environment configuration.

    - ai mode: AiService (runtime-backed, ADK-integrated via providers)
    - default: MockService (self-contained in-memory)

    Cached to reuse the instance across requests within the process.
    """
    app = request.app
    if _use_ai_mode():
        # Ensure ADKService exists in app.state (created in lifespan, but fallback here)
        adk_service = getattr(app.state, "adk_service", None)
        if adk_service is None:
            try:
                adk_service = ADKService()
                app.state.adk_service = adk_service
            except Exception as err:  # nosec B110
                # Surface the error later when used; for now create a minimal mock-like service
                raise RuntimeError(f"ADKService initialization failed: {err}") from err

        svc = getattr(app.state, "ai_service", None)
        if not isinstance(svc, AiService):
            svc = AiService(adk_service=adk_service)
            app.state.ai_service = svc
        return svc

    # Default: Mock mode
    svc = getattr(app.state, "mock_service", None)
    if not isinstance(svc, MockService):
        svc = MockService()
        app.state.mock_service = svc
    return svc
