from __future__ import annotations

import os
from functools import lru_cache

from hibikasu_agent.services.ai_service import AiService
from hibikasu_agent.services.base import ReviewServiceBase
from hibikasu_agent.services.mock_service import MockService


def _use_ai_mode() -> bool:
    mode = (os.getenv("HIBIKASU_API_MODE") or "").strip().lower()
    return mode == "ai"


@lru_cache(maxsize=2)
def get_service() -> ReviewServiceBase:
    """Provide a review service instance based on environment configuration.

    - ai mode: AiService (runtime-backed, ADK-integrated via providers)
    - default: MockService (self-contained in-memory)
    Cached to reuse the instance across requests within the process.
    """
    if _use_ai_mode():
        return AiService()
    return MockService()
