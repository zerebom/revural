from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from hibikasu_agent.api.dependencies import get_review_service
from hibikasu_agent.api.schemas.reviews import (
    AgentRole,
    ApplySuggestionResponse,
    DialogRequest,
    DialogResponse,
    ReviewRequest,
    ReviewResponse,
    ReviewSummaryResponse,
    StatusResponse,
    SuggestResponse,
    UpdateStatusRequest,
    UpdateStatusResponse,
)
from hibikasu_agent.constants.agents import SPECIALIST_DEFINITIONS
from hibikasu_agent.services.base import AbstractReviewService
from hibikasu_agent.utils.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/reviews", response_model=ReviewResponse)
async def start_review(
    req: ReviewRequest,
    background_tasks: BackgroundTasks,
    service: AbstractReviewService = Depends(get_review_service),
) -> ReviewResponse:
    # 1) セッションだけ先に作成（同期）
    review_id = service.new_review_session(req.prd_text, req.panel_type, selected_agents=req.selected_agent_roles)
    # 2) 重い計算はバックグラウンドへ（同期ラッパーを登録）
    background_tasks.add_task(service.kickoff_review, review_id=review_id)
    logger.info(
        "start_review accepted",
        extra={"review_id": review_id, "panel_type": req.panel_type or "", "prd_len": len(req.prd_text or "")},
    )
    return ReviewResponse(review_id=review_id)


@router.get("/reviews/{review_id}", response_model=StatusResponse)
async def get_review(review_id: str, service: AbstractReviewService = Depends(get_review_service)) -> StatusResponse:
    data: dict[str, Any] = service.get_review_session(review_id)
    try:
        issues_count = len(data.get("issues") or []) if isinstance(data.get("issues"), list) else 0
        logger.debug(
            "get_review polled",
            extra={"review_id": review_id, "status": data.get("status"), "issues_count": issues_count},
        )
    except Exception:  # nosec B110
        pass
    return StatusResponse.model_validate(data)


@router.post("/reviews/{review_id}/issues/{issue_id}/dialog", response_model=DialogResponse)
async def issue_dialog(
    review_id: str,
    issue_id: str,
    req: DialogRequest,
    service: AbstractReviewService = Depends(get_review_service),
) -> DialogResponse:
    issue = service.find_issue(review_id, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    text = await service.answer_dialog(review_id, issue_id, req.question_text)
    return DialogResponse(response_text=text)


@router.post("/reviews/{review_id}/issues/{issue_id}/suggest", response_model=SuggestResponse)
async def issue_suggest(
    review_id: str,
    issue_id: str,
    service: AbstractReviewService = Depends(get_review_service),
) -> SuggestResponse:
    issue = service.find_issue(review_id, issue_id)
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
async def issue_apply_suggestion(
    review_id: str,
    issue_id: str,
    service: AbstractReviewService = Depends(get_review_service),
) -> ApplySuggestionResponse:
    _ = (review_id, issue_id, service)
    return ApplySuggestionResponse(status="success")


@router.patch(
    "/reviews/{review_id}/issues/{issue_id}/status",
    response_model=UpdateStatusResponse,
)
async def update_issue_status_endpoint(
    review_id: str,
    issue_id: str,
    req: UpdateStatusRequest,
    service: AbstractReviewService = Depends(get_review_service),
) -> UpdateStatusResponse:
    success = service.update_issue_status(review_id, issue_id, req.status)
    if not success:
        raise HTTPException(status_code=404, detail="Issue not found")
    return UpdateStatusResponse(status="success")


@router.get("/reviews/{review_id}/summary", response_model=ReviewSummaryResponse)
async def get_review_summary(
    review_id: str, service: AbstractReviewService = Depends(get_review_service)
) -> ReviewSummaryResponse:
    data = service.get_review_summary(review_id)
    return ReviewSummaryResponse.model_validate(data)


@router.get("/agents/roles", response_model=list[AgentRole])
async def get_agent_roles() -> list[AgentRole]:
    """Get available agent roles for review selection.

    Returns enriched agent information from SpecialistDefinition (Single Source of Truth).
    """

    return [
        AgentRole(
            role=definition.role,
            display_name=definition.display_name,
            description=definition.review_description,
            role_label=definition.role_label,
            bio=definition.bio,
            tags=definition.tags,
            avatar_url=definition.avatar_url,
        )
        for definition in SPECIALIST_DEFINITIONS
    ]
