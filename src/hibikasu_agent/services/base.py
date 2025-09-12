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
    async def start_review_process(self, prd_text: str, panel_type: str | None = None) -> str:
        """Start a new review process and return its session ID.

        This method combines session creation and computation kickoff into a single operation.

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
