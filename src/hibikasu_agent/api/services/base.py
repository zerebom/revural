from __future__ import annotations

from typing import Any, Protocol


class ReviewService(Protocol):
    """Protocol for review services used by the API layer."""

    # simple in-memory store (implementation-defined shape)
    reviews_in_memory: dict[str, dict[str, Any]]

    def new_review_session(self, prd_text: str, panel_type: str | None = None) -> str: ...

    def get_review_session(self, review_id: str) -> dict[str, Any]: ...

    def find_issue(self, review_id: str, issue_id: str) -> Any | None: ...
