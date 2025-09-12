from __future__ import annotations

from typing import Any

from hibikasu_agent.api.schemas import Issue
from hibikasu_agent.services import runtime as ai_runtime
from hibikasu_agent.services.base import AbstractReviewService


class AiService(AbstractReviewService):
    """AI-backed review service using the existing runtime module.

    This class adapts the module-level runtime functions to the
    AbstractReviewService interface for DI-friendly usage.
    """

    def new_review_session(self, prd_text: str, panel_type: str | None = None) -> str:
        return ai_runtime.new_review_session(prd_text, panel_type)

    def get_review_session(self, review_id: str) -> dict[str, Any]:
        return ai_runtime.get_review_session(review_id)

    def find_issue(self, review_id: str, issue_id: str) -> Issue | None:
        return ai_runtime.find_issue(review_id, issue_id)

    # Expose kickoff to enable BackgroundTasks scheduling
    def kickoff_compute(self, review_id: str) -> None:
        return ai_runtime.kickoff_compute(review_id)

    # Convenience proxies retained for tests and providers
    @staticmethod
    def set_review_impl(func):  # (prd_text: str) -> list[Issue]
        return ai_runtime.set_review_impl(func)

    @staticmethod
    def has_review_impl() -> bool:
        return ai_runtime.has_review_impl()

    @property
    def reviews_in_memory(self) -> dict[str, dict[str, Any]]:
        return ai_runtime.reviews_in_memory
