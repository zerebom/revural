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
    comment: str = Field(description="The review comment text")
    original_text: str = Field(description="Quoted text from original PRD")


class FinalIssue(BaseModel):
    """オーケストレーターによって拡充された最終的な指摘事項のフォーマット。

    集約された指摘事項に対するユーザーの希望する出力形式を反映しています。
    """

    issue_id: str = Field(description="一意の指摘ID")
    priority: int = Field(description="優先順位（1が最高,2が中, 3が低）")
    agent_name: str = Field(description="指摘を挙げた専門家の名前")
    summary: str = Field(
        default="",
        description="アコーディオンのヘッダーに表示するための一文程度の短い要約",
    )
    comment: str = Field(description="詳細や論理的根拠を含む、レビューコメントの全文")
    original_text: str = Field(description="元のPRDから引用されたテキスト")
    status: str = Field(default="pending", description="指摘のステータス（例: pending, done, later）")


class FinalIssuesResponse(BaseModel):
    """Wrapper for returning a list of final issues."""

    final_issues: list[FinalIssue] = Field(description="Aggregated and prioritized issues")


# Shared output schema across specialist agents
class IssueItem(BaseModel):
    """Minimal issue item produced by specialists."""

    priority: int = Field(ge=1, le=3)
    summary: str = Field(description="指摘内容を20文字程度で要約した短いタイトル")
    comment: str = Field(min_length=1)
    original_text: str = Field(default="")


class IssuesResponse(BaseModel):
    """Wrapper for specialist agent outputs."""

    issues: list[IssueItem] = Field(description="List of issues found in the PRD")


class SpecialistIssue(BaseModel):
    """Model for individual issue from the legacy orchestrator tool."""

    priority: int = Field(ge=1, le=3)
    description: str = Field(min_length=1)
    recommendation: str = Field(default="")
    category: str = Field(default="")


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
