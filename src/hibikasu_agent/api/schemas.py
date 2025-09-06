from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    """Request body for starting a review session."""

    prd_text: str = Field(description="PRD full text for review")
    # architecture.md 10.2 requires prd_text; panel_type is reserved
    panel_type: str | None = Field(
        default=None,
        description="Panel type (optional)",
    )


class ReviewResponse(BaseModel):
    """Response body returned by POST /reviews."""

    review_id: str


class Issue(BaseModel):
    """Minimal issue model per API spec (architecture.md 10.1)."""

    issue_id: str
    priority: int
    agent_name: str
    comment: str
    original_text: str


class StatusResponse(BaseModel):
    """Polling response for GET /reviews/{review_id}."""

    status: Literal["processing", "completed", "failed", "not_found"]
    issues: list[Issue] | None = None


class DialogRequest(BaseModel):
    question_text: str


class DialogResponse(BaseModel):
    response_text: str


class SuggestResponse(BaseModel):
    suggested_text: str
    target_text: str


class ApplySuggestionResponse(BaseModel):
    status: Literal["success", "failed"]
