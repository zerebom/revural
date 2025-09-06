from __future__ import annotations

import os


def api_mode() -> str:
    """Return API mode: 'mock' (default) or 'ai'.

    Controlled by env var `HIBIKASU_API_MODE` or `ENABLE_AI` (legacy boolean).
    """
    mode = os.getenv("HIBIKASU_API_MODE", "").strip().lower()
    if mode in {"mock", "ai"}:
        return mode
    # fallback: legacy boolean flag
    if os.getenv("ENABLE_AI", "").strip().lower() in {"1", "true", "yes", "on"}:
        return "ai"
    return "mock"


def is_ai_mode() -> bool:
    return api_mode() == "ai"
