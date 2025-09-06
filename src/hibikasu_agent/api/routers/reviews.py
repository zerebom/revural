from __future__ import annotations

from typing import Any

from fastapi import APIRouter

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

router = APIRouter()


async def start_review(req: ReviewRequest) -> ReviewResponse:
    review_id = get_service().new_review_session(req.prd_text, req.panel_type)
    return ReviewResponse(review_id=review_id)


async def get_review(review_id: str) -> StatusResponse:
    data: dict[str, Any] = get_service().get_review_session(review_id)
    return StatusResponse.model_validate(data)


async def issue_dialog(review_id: str, issue_id: str, req: DialogRequest) -> DialogResponse:
    issue = get_service().find_issue(review_id, issue_id)
    if issue is None:
        return DialogResponse(
            response_text=(
                "該当する論点が見つかりませんでしたが、一般的な観点としては、処理の分割やバルク処理の検討が有効です。"
            )
        )
    return DialogResponse(
        response_text=(
            "ご質問ありがとうございます。"
            f"（ご質問:『{req.question_text}』）"
            f"『{issue.original_text}』に関しては、バルク保存や"
            "制限値の設定を検討すると良いでしょう。"
        )
    )


async def issue_suggest(review_id: str, issue_id: str) -> SuggestResponse:
    issue = get_service().find_issue(review_id, issue_id)
    target_text = issue.original_text if issue else "(対象テキスト未取得)"
    suggested = (
        "PRDの要件に以下を追記することを推奨します。"
        "『ユーザー体験を損なわないため、一度に保存できる項目は最大100個までとする。』"
    )
    return SuggestResponse(suggested_text=suggested, target_text=target_text)


async def issue_apply_suggestion(review_id: str, issue_id: str) -> ApplySuggestionResponse:
    _ = issue_id
    if review_id not in get_service().reviews_in_memory:
        return ApplySuggestionResponse(status="success")
    return ApplySuggestionResponse(status="success")


# Register routes explicitly to avoid mypy decorator issues
router.add_api_route("/reviews", start_review, methods=["POST"], response_model=ReviewResponse)
router.add_api_route("/reviews/{review_id}", get_review, methods=["GET"], response_model=StatusResponse)
router.add_api_route(
    "/reviews/{review_id}/issues/{issue_id}/dialog",
    issue_dialog,
    methods=["POST"],
    response_model=DialogResponse,
)
router.add_api_route(
    "/reviews/{review_id}/issues/{issue_id}/suggest",
    issue_suggest,
    methods=["POST"],
    response_model=SuggestResponse,
)
router.add_api_route(
    "/reviews/{review_id}/issues/{issue_id}/apply_suggestion",
    issue_apply_suggestion,
    methods=["POST"],
    response_model=ApplySuggestionResponse,
)
