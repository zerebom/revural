from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class IssueSpan(BaseModel):
    """Character index range of the highlighted text in the PRD.

    Indices are 0-based, half-open interval [start_index, end_index).
    """

    start_index: int
    end_index: int


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
    summary: str = Field(default="")
    comment: str
    original_text: str
    # Optional highlight span into the original PRD text
    span: IssueSpan | None = None
    # Optional per-issue status managed by the client workflow
    status: str | None = None


class ReviewSession(BaseModel):
    """Internal model representing a review session state."""

    created_at: float
    status: Literal["processing", "completed", "failed", "not_found"]
    issues: list[Issue] | None = None
    prd_text: str
    panel_type: str | None = None
    polls: int = 0
    progress: float | None = None
    phase: str | None = None
    phase_message: str | None = None
    eta_seconds: int | None = None
    expected_agents: list[str] | None = None
    completed_agents: list[str] | None = None


class StatusResponse(BaseModel):
    """Polling response for GET /reviews/{review_id}."""

    status: Literal["processing", "completed", "failed", "not_found"]
    issues: list[Issue] | None = None
    # Include original PRD text so the frontend can hydrate state on reload
    prd_text: str | None = None
    progress: float | None = None
    phase: str | None = None
    phase_message: str | None = None
    eta_seconds: int | None = None
    expected_agents: list[str] | None = None
    completed_agents: list[str] | None = None


class DialogRequest(BaseModel):
    question_text: str


class DialogResponse(BaseModel):
    response_text: str


class SuggestResponse(BaseModel):
    suggested_text: str
    target_text: str


class ApplySuggestionResponse(BaseModel):
    status: Literal["success", "failed"]


class UpdateStatusRequest(BaseModel):
    """Request body for updating an issue status."""

    status: str


class UpdateStatusResponse(BaseModel):
    """Response for status update operations."""

    status: Literal["success", "failed"]


class StatusCount(BaseModel):
    """Aggregated count per issue status."""

    key: str
    label: str
    count: int


class AgentCount(BaseModel):
    """Aggregated count per agent."""

    agent_name: str
    count: int


class SummaryStatistics(BaseModel):
    """Statistics block for the summary view."""

    total_issues: int = 0
    status_counts: list[StatusCount] = Field(default_factory=list)
    agent_counts: list[AgentCount] = Field(default_factory=list)


class ReviewSummaryResponse(BaseModel):
    """Response payload for the summary endpoint."""

    status: Literal["processing", "completed", "failed", "not_found"]
    statistics: SummaryStatistics
    issues: list[Issue]
