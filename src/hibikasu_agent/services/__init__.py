"""Application service layer package.

This package contains:
- runtime: in-memory state + orchestration hooks used by the API layer
- providers: concrete engines (ADK, mock) that plug into the runtime
"""

from __future__ import annotations

__all__ = [
    "runtime",
]
