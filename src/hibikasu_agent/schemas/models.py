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
    """オーケストレーターによって拡充された最終的な指摘事項のフォーマット。

    集約された指摘事項に対するユーザーの希望する出力形式を反映しています。
    """

    issue_id: str = Field(description="一意の指摘ID")
    priority: int = Field(description="優先順位（1が最高,2が中, 3が低）")
    agent_name: str = Field(description="指摘を挙げた専門家の名前")
    severity: str = Field(description="深刻度（高/中/低）")
    summary: str = Field(
        default="",
        description="アコーディオンのヘッダーに表示するための一文程度の短い要約",
    )
    comment: str = Field(description="詳細や論理的根拠を含む、レビューコメントの全文")
    original_text: str = Field(description="元のPRDから引用されたテキスト")


class FinalIssuesResponse(BaseModel):
    """Wrapper for returning a list of final issues."""

    final_issues: list[FinalIssue] = Field(description="Aggregated and prioritized issues")


# Shared output schema across specialist agents
class IssueItem(BaseModel):
    """Minimal issue item produced by specialists.

    Accepts a broader set of severity labels and normalizes them to
    one of: High / Mid / Low. Case-insensitive. Common synonyms like
    major/medium/minor are supported.
    """

    severity: str = Field()
    comment: str = Field(min_length=1)
    original_text: str = Field(default="")

    @staticmethod
    def _map_severity(value: str) -> str:
        v = (value or "").strip().lower()
        if v in {"high", "major", "critical", "severe"}:
            return "High"
        if v in {"mid", "medium", "moderate"}:
            return "Mid"
        if v in {"low", "minor", "trivial"}:
            return "Low"
        # Fallback: try title-case known values; otherwise default to Mid to avoid hard failure
        if v and v.title() in {"High", "Mid", "Low"}:
            return v.title()
        return "Mid"

    def normalize_severity(self) -> str:
        return self._map_severity(self.severity)


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


# ====== Minimal models for PersonaAgent typing ======


class Persona(BaseModel):
    """Minimal persona profile used by PersonaAgent."""

    name: str
    age: int
    occupation: str


class Utterance(BaseModel):
    """Conversation utterance used in PersonaAgent history."""

    speaker: str
    content: str
    timestamp: str | None = None
