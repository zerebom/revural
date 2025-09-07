from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from hibikasu_agent.api.schemas import (
    ApplySuggestionResponse,
    DialogRequest,
    DialogResponse,
    ReviewRequest,
    ReviewResponse,
    StatusResponse,
    SuggestResponse,
)
from hibikasu_agent.api.services import get_service
from hibikasu_agent.services.providers.adk import answer_dialog as adk_answer_dialog

router = APIRouter()


@router.post("/reviews", response_model=ReviewResponse)
async def start_review(req: ReviewRequest, background_tasks: BackgroundTasks) -> ReviewResponse:
    svc = get_service()
    review_id = svc.new_review_session(req.prd_text, req.panel_type)
    # If AI service provides kickoff, schedule compute asynchronously
    kickoff = getattr(svc, "kickoff_compute", None)
    if callable(kickoff):
        background_tasks.add_task(kickoff, review_id)
    return ReviewResponse(review_id=review_id)


@router.get("/reviews/{review_id}", response_model=StatusResponse)
async def get_review(review_id: str) -> StatusResponse:
    data: dict[str, Any] = get_service().get_review_session(review_id)
    return StatusResponse.model_validate(data)


@router.post("/reviews/{review_id}/issues/{issue_id}/dialog", response_model=DialogResponse)
async def issue_dialog(review_id: str, issue_id: str, req: DialogRequest) -> DialogResponse:
    issue = get_service().find_issue(review_id, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    text = await adk_answer_dialog(review_id, issue_id, req.question_text)
    return DialogResponse(response_text=text)


@router.post("/reviews/{review_id}/issues/{issue_id}/suggest", response_model=SuggestResponse)
async def issue_suggest(review_id: str, issue_id: str) -> SuggestResponse:
    issue = get_service().find_issue(review_id, issue_id)
    target_text = issue.original_text if issue else "(対象テキスト未取得)"
    suggested = (
        "PRDの要件に以下を追記することを推奨します。"
        "『ユーザー体験を損なわないため、一度に保存できる項目は最大100個までとする。』"
    )
    return SuggestResponse(suggested_text=suggested, target_text=target_text)


@router.post(
    "/reviews/{review_id}/issues/{issue_id}/apply_suggestion",
    response_model=ApplySuggestionResponse,
)
async def issue_apply_suggestion(review_id: str, issue_id: str) -> ApplySuggestionResponse:
    _ = issue_id
    if review_id not in get_service().reviews_in_memory:
        return ApplySuggestionResponse(status="success")
    return ApplySuggestionResponse(status="success")
