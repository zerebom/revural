from __future__ import annotations

from typing import Any

class BaseModel:
    def __init__(self, **data: Any) -> None: ...
    def model_dump(self) -> dict[str, Any]: ...

class Issue(BaseModel):
    issue_id: str | None
    priority: int
    agent_name: str
    agent_avatar: str
    severity: str
    comment: str
    original_text: str

class FinalIssue(BaseModel):
    issue_id: str
    priority: int
    agent_name: str
    severity: str
    comment: str
    original_text: str

class FinalIssuesResponse(BaseModel):
    final_issues: list[FinalIssue]

class IssueItem(BaseModel):
    severity: str
    comment: str
    original_text: str
    def normalize_severity(self) -> str: ...

class IssuesResponse(BaseModel):
    issues: list[IssueItem]

class SpecialistIssue(BaseModel):
    severity: str
    description: str
    recommendation: str
    category: str
    def normalize_severity(self) -> str: ...

class ReviewSession(BaseModel):
    review_id: str
    prd_text: str
    panel_type: str
    final_issues: list[Issue]
    created_at: str

class ChatMessage(BaseModel):
    message_id: str
    issue_id: str
    sender: str
    content: str
    timestamp: str

class SuggestionResponse(BaseModel):
    suggested_text: str
    target_text: str

class ApplyResponse(BaseModel):
    status: str
    message: str | None

class Persona(BaseModel):
    name: str
    age: int
    occupation: str

class Utterance(BaseModel):
    speaker: str
    content: str
    timestamp: str | None
