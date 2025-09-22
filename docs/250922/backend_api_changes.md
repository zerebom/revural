# バックエンド変更案（API/モデル）

対象: FastAPI（`src/hibikasu_agent/api/routers/reviews.py` 他）

## 1. レビュー開始API: 選択ロールの受け取り
- 変更: `POST /reviews` のリクエストに `selected_agent_roles?: string[]` を追加。
- 受領後、`AiService.new_review_session(..., selected_agents=selected_agent_roles)` に引き渡し。

### 変更イメージ（スキーマ）
```python
# src/hibikasu_agent/api/schemas/reviews.py
class ReviewRequest(BaseModel):
    prd_text: str
    panel_type: str | None = None
    selected_agent_roles: list[str] | None = None  # 追加
```

```python
# src/hibikasu_agent/api/routers/reviews.py
@router.post("/reviews", response_model=ReviewResponse)
async def start_review(req: ReviewRequest, background_tasks: BackgroundTasks, service: AbstractReviewService = Depends(get_review_service)) -> ReviewResponse:
    review_id = service.new_review_session(
        req.prd_text,
        req.panel_type,
        selected_agents=req.selected_agent_roles,
    )
    background_tasks.add_task(service.kickoff_review, review_id=review_id)
    return ReviewResponse(review_id=review_id)
```

- 実行経路は既存で対応済み:
  - `AiService.new_review_session(..., selected_agents=...)` → `ReviewRuntimeSession.selected_agent_roles` に保存。
  - `AiService.kickoff_review` 内で `self._review_runner.run_blocking(..., selected_agents=sess.selected_agent_roles)`。
  - `AdkReviewRunner` → `ADKService.run_review_async(..., selected_agents=...)`。
  - `create_parallel_review_agent(selected_agents=...)` で定義フィルタリング済み。

## 2. 利用可能ロールの取得API
- 追加: `GET /agents/roles`
- 返却: `[{ role: string, display_name: string, description: string }]`
- 実装元: `hibikasu_agent.constants.agents.SPECIALIST_DEFINITIONS` から生成。

```python
# 返却例
[
  {"role": "engineer", "display_name": "Engineer Specialist", "description": "バックエンドエンジニアの専門的観点からPRDをレビュー"},
  {"role": "ux_designer", ...},
  ...
]
```

## 3. 体制プリセット取得API（任意だが推奨）
- 追加: `GET /agent-presets`
- 返却: `[{ key: string, name: string, roles: string[] }]`
- 実装方法: サーバー側の定数 or 設定ファイル（将来はDB）で定義。

```json
[
  {"key": "prd_review", "name": "PRDレビュー", "roles": ["engineer", "ux_designer", "qa_tester", "pm"]},
  {"key": "legal_check", "name": "法務チェック", "roles": ["legal", "security", "pm"]},
  {"key": "blog_check", "name": "ブログチェック", "roles": ["copywriter", "marketing", "ux_designer"]}
]
```

※ 現状のロールセットは 4 名に限定されるため、まずは既存ロールのみで返し、将来の追加に備えてAPI設計だけ先に用意。

## 4. ステータスAPIの表示名サポート（任意）
- 既存の `StatusResponse.expected_agents` は agent_key ベース。フロントで `AGENT_DISPLAY_NAMES` による変換で十分。
- ただしUX向上のため、`expected_agent_display_names?: string[]` を追加する案もあり（互換維持）。

## 5. 型/モデルの差分
- `ReviewRequest` に `selected_agent_roles` を追加。
- 既存 `ReviewRuntimeSession` は `selected_agent_roles` を保持済み（変更不要）。

## 6. テスト観点
- `tests/api/test_reviews_endpoints.py` に以下を追加:
  - `POST /reviews` に `selected_agent_roles` を含めても 200/正常開始となる。
  - ポーリング完了後、`expected_agents` が選択内容（に対応する `agent_key`）に絞られていること。
- `tests/unit/test_agent_selection.py` は既に `create_parallel_review_agent(selected_agents=...)` の動作を網羅。

## 7. 移行/後方互換
- `selected_agent_roles` 未指定時は従来通り全員（4名）実行。
- 新APIの追加は非破壊的。フロントから段階的に移行可能。
