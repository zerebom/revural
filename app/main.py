from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    ApplySuggestionResponse,
    DialogRequest,
    DialogResponse,
    ReviewRequest,
    ReviewResponse,
    StatusResponse,
    SuggestResponse,
)
from app.services import (
    find_issue,
    get_review_session,
    new_review_session,
    reviews_in_memory,
)


def _allowed_origins_from_env() -> list[str]:
    env_val = os.getenv("CORS_ALLOW_ORIGINS")
    if env_val:
        return [o.strip() for o in env_val.split(",") if o.strip()]
    # sensible defaults for local Next.js/Vite
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


app = FastAPI(title="Hibikasu PRD Reviewer API (Mock)", version="0.1.0-mock")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins_from_env(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/reviews", response_model=ReviewResponse)
async def start_review(req: ReviewRequest) -> ReviewResponse:
    review_id = new_review_session(req.prd_text, req.panel_type)
    return ReviewResponse(review_id=review_id)


@app.get("/reviews/{review_id}", response_model=StatusResponse)
async def get_review(review_id: str) -> StatusResponse:
    data = get_review_session(review_id)
    # Pydantic model coercion for Any -> Issue list
    return StatusResponse.model_validate(data)


@app.post(
    "/reviews/{review_id}/issues/{issue_id}/dialog",
    response_model=DialogResponse,
)
async def issue_dialog(review_id: str, issue_id: str, req: DialogRequest) -> DialogResponse:
    issue = find_issue(review_id, issue_id)
    if issue is None:
        # still return mocked text even if not found, to keep FE unblocked
        return DialogResponse(
            response_text=(
                "該当する論点が見つかりませんでしたが、一般的な観点としては、"
                "処理の分割やバルク処理の検討が有効です。"
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


@app.post(
    "/reviews/{review_id}/issues/{issue_id}/suggest",
    response_model=SuggestResponse,
)
async def issue_suggest(review_id: str, issue_id: str) -> SuggestResponse:
    issue = find_issue(review_id, issue_id)
    target_text = issue.original_text if issue else "(対象テキスト未取得)"
    suggested = (
        "PRDの要件に以下を追記することを推奨します。"
        "『ユーザー体験を損なわないため、一度に保存できる項目は最大100個までとする。』"
    )
    return SuggestResponse(suggested_text=suggested, target_text=target_text)


@app.post(
    "/reviews/{review_id}/issues/{issue_id}/apply_suggestion",
    response_model=ApplySuggestionResponse,
)
async def issue_apply_suggestion(review_id: str, _issue_id: str) -> ApplySuggestionResponse:
    # For mock, we simply return success without mutating PRD text
    if review_id not in reviews_in_memory:
        # still succeed to keep FE flow simple
        return ApplySuggestionResponse(status="success")
    return ApplySuggestionResponse(status="success")
