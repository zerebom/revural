from __future__ import annotations

import os

from fastapi import Request

from hibikasu_agent.services.ai_service import AiService
from hibikasu_agent.services.base import AbstractReviewService
from hibikasu_agent.services.mock_service import MockService


def _use_ai_mode() -> bool:
    mode = (os.getenv("HIBIKASU_API_MODE", "ai") or "").strip().lower()
    return mode == "ai"


def get_review_service(request: Request) -> AbstractReviewService:
    """Provide a review service instance based on environment configuration.

    - ai mode: AiService (runtime-backed, ADK-integrated via providers)
    - default: MockService (self-contained in-memory)

    Cached to reuse the instance across requests within the process.
    """
    app = request.app
    if _use_ai_mode():
        svc = getattr(app.state, "ai_service", None)
        if not isinstance(svc, AiService):
            raise RuntimeError("AiService is not initialized. Ensure lifespan initialized AI services.")
        return svc

    # Default: Mock mode
    svc = getattr(app.state, "mock_service", None)
    if not isinstance(svc, MockService):
        svc = MockService()
        app.state.mock_service = svc
    return svc
