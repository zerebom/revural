"""Backwards-compat API service accessor.

Routers call `get_service()` to obtain the current runtime-backed
service object. The detailed service interface is defined in
`hibikasu_agent.services.base` for the new DI path, but this module
keeps a minimal shim so existing imports continue to work until DI
migration is complete.
"""

from __future__ import annotations

from hibikasu_agent.services import runtime as ai_service


def get_service():  # runtime provides module-level functions used by routers
    return ai_service
