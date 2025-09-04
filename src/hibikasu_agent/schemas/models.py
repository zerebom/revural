"""Data models for Hibikasu PRD Reviewer."""

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class Issue(BaseModel):
    """Represents a single review issue/comment."""

    issue_id: str | None = Field(default=None, description="Unique issue ID")
    priority: int = Field(description="Priority for user presentation")
    agent_name: str = Field(description="Name of the agent that generated this issue")
    agent_avatar: str = Field(description="Avatar/icon identifier for the agent")
    severity: str = Field(description="Severity level (High/Mid/Low)")
    comment: str = Field(description="The review comment text")
    original_text: str = Field(description="Quoted text from original PRD")


class FinalIssue(BaseModel):
    """Final issue format enriched by the orchestrator.

    This mirrors the user's desired output shape for aggregated issues.
    """

    issue_id: str = Field(description="Unique issue ID")
    priority: int = Field(description="Priority order (1 = highest)")
    agent_name: str = Field(description="Name of the specialist who raised it")
    severity: str = Field(description="Severity level (High/Mid/Low)")
    comment: str = Field(description="Review comment text")
    original_text: str = Field(description="Quoted text from original PRD")


class FinalIssuesResponse(BaseModel):
    """Wrapper for returning a list of final issues."""

    final_issues: list[FinalIssue] = Field(
        description="Aggregated and prioritized issues"
    )


# Shared output schema across specialist agents
class IssueItem(BaseModel):
    """Minimal issue item produced by specialists.

    Used by specialist LlmAgents and parallel aggregation.
    """

    severity: str = Field(pattern="^(High|Mid|Low|Medium)$")
    comment: str = Field(min_length=1)
    original_text: str = Field(default="")

    def normalize_severity(self) -> str:
        return "Mid" if self.severity == "Medium" else self.severity


class IssuesResponse(BaseModel):
    """Wrapper for specialist agent outputs."""

    issues: list[IssueItem] = Field(description="List of issues found in the PRD")


class SpecialistIssue(BaseModel):
    """Model for individual issue from the legacy orchestrator tool.

    This aligns with the existing orchestrator/tools.py expectations.
    """

    severity: str = Field(pattern="^(High|Mid|Low|Medium)$")
    description: str = Field(min_length=1)
    recommendation: str = Field(default="")
    category: str = Field(default="")

    def normalize_severity(self) -> str:
        return "Mid" if self.severity == "Medium" else self.severity


class ReviewSession(BaseModel):
    """Represents a complete PRD review session."""

    review_id: str = Field(default_factory=lambda: str(uuid4()))
    prd_text: str = Field(description="Full text of the PRD being reviewed")
    panel_type: str = Field(description="Type of review panel (e.g., 'Webサービス')")
    final_issues: list[Issue] = Field(description="Final prioritized list of issues")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ChatMessage(BaseModel):
    """Represents a message in the chat dialogue for issue discussion."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    issue_id: str = Field(description="ID of the issue being discussed")
    sender: str = Field(description="Sender: 'user' or agent name")
    content: str = Field(description="Message content")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SuggestionResponse(BaseModel):
    """Response model for modification suggestions."""

    suggested_text: str = Field(description="Suggested modification text")
    target_text: str = Field(description="Original text to be modified")


class ApplyResponse(BaseModel):
    """Response model for applying suggestions."""

    status: str = Field(description="Application status (success/error)")
    message: str | None = Field(default=None, description="Optional status message")
