"""Abstract base class for review services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbstractReviewService(ABC):
    """Abstract base class for review services.

    Defines the interface that all review service implementations must follow.
    This ensures consistency across different implementations (AI, Mock, etc.).
    """

    @abstractmethod
    def new_review_session(self, prd_text: str, panel_type: str | None = None) -> str:
        """Create a new review session and return its ID.

        Args:
            prd_text: The PRD text to review
            panel_type: Optional panel type for specialized reviews

        Returns:
            A unique session ID string
        """
        ...

    @abstractmethod
    def get_review_session(self, review_id: str) -> dict[str, Any]:
        """Get the current status and data of a review session.

        Args:
            review_id: The review session ID

        Returns:
            A dictionary containing session status and data
        """
        ...

    @abstractmethod
    def find_issue(self, review_id: str, issue_id: str) -> Any | None:
        """Find a specific issue within a review session.

        Args:
            review_id: The review session ID
            issue_id: The issue ID to find

        Returns:
            The issue data if found, None otherwise
        """
        ...

    @abstractmethod
    def kickoff_compute(self, review_id: str) -> None:
        """Start the computation of issues for a review session.

        This method may run synchronously or asynchronously depending on
        the implementation. Routers may schedule this via FastAPI BackgroundTasks.

        Args:
            review_id: The review session ID to compute issues for
        """
        ...
