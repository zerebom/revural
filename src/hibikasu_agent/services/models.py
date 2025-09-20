from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from hibikasu_agent.api.schemas import Issue


class ReviewRuntimeSession(BaseModel):
    """Internal runtime/session state for API review processing.

    Kept minimal and focused on API needs. Not exposed publicly.
    """

    created_at: float = Field(description="Epoch seconds when the session was created")
    status: Literal["processing", "completed", "failed"] = Field(default="processing")
    issues: list[Issue] | None = Field(default=None, description="Computed issues when completed")
    prd_text: str = Field(default="")
    panel_type: str | None = Field(default=None)
    error: str | None = Field(default=None, description="Error details when status is failed")
    progress: float = Field(default=0.0, description="Overall completion ratio (0.0-1.0)")
    phase: str = Field(default="processing", description="Current processing phase identifier")
    phase_message: str | None = Field(default=None, description="Human readable phase message")
    eta_seconds: int | None = Field(default=None, description="Estimated remaining time in seconds")
    expected_agents: list[str] = Field(default_factory=list, description="Agent names scheduled to run")
    completed_agents: list[str] = Field(default_factory=list, description="Agent names that finished")
