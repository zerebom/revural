"""Abstract base class for review services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbstractReviewService(ABC):
    """Abstract base class for review services.

    Defines the interface that all review service implementations must follow.
    This ensures consistency across different implementations (AI, Mock, etc.).
    """

    # start_review_process は撤廃。ルーターからは new_review_session + kickoff_review を使用する。

    @abstractmethod
    def new_review_session(self, prd_text: str, panel_type: str | None = None) -> str:
        """Create a new review session and return its ID."""
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
    async def answer_dialog(self, review_id: str, issue_id: str, question_text: str) -> str:
        """Answer a follow-up question for a specific issue in a review.

        Args:
            review_id: The review session ID
            issue_id: The issue ID within the review
            question_text: The user question

        Returns:
            The answer text
        """
        ...

    @abstractmethod
    def kickoff_review(self, review_id: str) -> None:
        """Kick off heavy review computation in background.

        This synchronous wrapper is suitable for FastAPI BackgroundTasks.
        It should call the provider's async review method via asyncio.run().
        """
        ...
