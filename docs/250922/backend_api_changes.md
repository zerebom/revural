# バックエンド変更案（API/モデル・更新）

対象: FastAPI（`src/hibikasu_agent/api/routers/reviews.py` 他）

本書はコード変更を含みません。API契約とバリデーション方針のみ更新し、既存実装の延長で成立させます。

## 1. レビュー開始API: 選択ロールの受け取り（非破壊拡張）
- 変更: `POST /reviews` のリクエストに `selected_agent_roles?: string[]` を追加（未指定は従来4名）。
- 受領後、`AiService.new_review_session(..., selected_agents=selected_agent_roles)` に引き渡し。

### リクエスト/レスポンス例
```json
// POST /reviews (Request)
{
  "prd_text": "...",
  "panel_type": null,
  "selected_agent_roles": ["engineer", "pm"]
}
```

```json
// POST /reviews (Response)
{ "review_id": "7f2b9b6e-..." }
```

## 2. ステータス取得API（既存）
- `GET /reviews/{review_id}` で進捗と担当者を返す。
- `expected_agents` / `completed_agents` は agent_key ベース（UIで表示名へ変換）。

```json
// 例: GET /reviews/{id}
{
  "status": "processing",
  "issues": null,
  "prd_text": "...",
  "progress": 0.35,
  "phase": "parallel_specialists",
  "phase_message": "2名の専門家がレビュー中",
  "eta_seconds": 24,
  "expected_agents": ["engineer_specialist", "pm_specialist"],
  "completed_agents": ["engineer_specialist"]
}
```

## 3. 役割/プリセット取得API（新設）
- 追加: `GET /agents/roles`
  - 返却: `[{ role: string, display_name: string, description: string }]`
  - 実装元: `hibikasu_agent.constants.agents.SPECIALIST_DEFINITIONS`

```json
[
  {"role": "engineer", "display_name": "Engineer Specialist", "description": "バックエンドエンジニアの専門的観点からPRDをレビュー"},
  {"role": "ux_designer", "display_name": "UX Designer Specialist", "description": "UXデザイナーの専門的観点からPRDをレビュー"},
  {"role": "qa_tester", "display_name": "QA Tester Specialist", "description": "QAテスターの専門的観点からPRDをレビュー"},
  {"role": "pm", "display_name": "PM Specialist", "description": "プロダクトマネージャーの専門的観点からPRDをレビュー"}
]
```

- 任意: `GET /agent-presets`
```json
[
  {"key": "prd_review", "name": "PRDレビュー", "roles": ["engineer", "ux_designer", "qa_tester", "pm"]}
]
```

## 4. サーバー側バリデーション/フォールバック
- `selected_agent_roles` 未指定 → 既定4ロール（従来挙動）
- 不正ロールが含まれる → 無視。1件以上の有効ロールがあれば採用、0件なら既定4ロールへフォールバック
- 上限超過（>4） → 先頭4件を採用（400/403は返さない）
- ログ出力に `selected_agent_roles` を含める（任意）

## 5. 表示名/プロフィールに関する扱い
- `expected_agents` は agent_key で返却。表示名への変換はUIで実施（`AGENT_DISPLAY_NAMES` 等）。
- 名前（日本語）/短いbio（約80字）/タグ（最大3）はUI用メタデータであり、当面はAPI契約に含めない（将来 `GET /agents/profiles` での拡張余地あり）。

## 6. テスト観点（サーバー）
- `POST /reviews` に選択ロールを付与しても 200/正常開始。
- ポーリング完了後、`expected_agents` が選択内容（に対応する `agent_key`）に絞られる。
- 不正ロール混在時のフォールバック、上限制御の確認。

## 7. 移行/後方互換・ロールアウト
- 後方互換: `selected_agent_roles` 未指定でも従来通り動作。
- UI側はフィーチャーフラグ下で段階露出可能。既存の固定4名体験と併存。
