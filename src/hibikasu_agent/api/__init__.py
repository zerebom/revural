"""API package for Hibikasu PRD Reviewer (mock endpoints).

Expose `ai_services` as a package attribute so that tests can import
`from hibikasu_agent.api import ai_services` without requiring a physical
submodule file.
"""

from __future__ import annotations

from hibikasu_agent.services import runtime as ai_services

__all__ = [
    "ai_services",
]
