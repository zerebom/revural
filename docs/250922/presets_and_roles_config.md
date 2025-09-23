# プリセット/ロール定義方針（提案）

## 1. 現状のロール（実装済み）
- role: `engineer` / agent_key: `engineer_specialist` / state_key: `engineer_issues`
- role: `ux_designer` / agent_key: `ux_designer_specialist` / state_key: `ux_designer_issues`
- role: `qa_tester` / agent_key: `qa_tester_specialist` / state_key: `qa_tester_issues`
- role: `pm` / agent_key: `pm_specialist` / state_key: `pm_issues`

出典: `src/hibikasu_agent/constants/agents.py` の `SPECIALIST_DEFINITIONS`
- 表示名: `AGENT_DISPLAY_NAMES`
- ロール辞書: `ROLE_TO_DEFINITION`

## 2. 追加ロールの設計指針（将来拡張）
- 例: `legal`, `security`, `copywriter`, `marketing` など
- 追加時は以下を定義:
  - `SpecialistDefinition(role, agent_key, state_key, display_name, review_description)` のタプルに追加
  - `prompts/agents.toml` に各ロールの `instruction_review` / `instruction_chat` を追加
  - 既存の `create_specialists_from_config` / `create_role_agents` が自動で拾う

### TOML例（抜粋）
```toml
[legal]
instruction_review = "法務観点でのレビュー方針..."
instruction_chat = "法務に関するQ&A方針..."

[security]
instruction_review = "セキュリティ観点でのレビュー方針..."
instruction_chat = "セキュリティQ&A方針..."
```

## 3. 体制プリセットの定義
- 取得API: `GET /agent-presets`（サーバー定数で良い）
- 返却スキーマ: `{ key: string, name: string, roles: string[] }[]`

### 初期プリセット案
- `prd_review`: PRDレビュー → `["engineer", "ux_designer", "qa_tester", "pm"]`
- `legal_check`: 法務チェック → `["legal", "security", "pm"]`（ロール追加後に有効化）
- `blog_check`: ブログチェック → `["copywriter", "marketing", "ux_designer"]`（ロール追加後に有効化）

## 4. APIとフロントの連携
- `GET /agents/roles` で利用可能ロール一覧を取得し、カード描画
- `GET /agent-presets` でプリセット取得 → 選択時に `selectedRoles` を置換
- `POST /reviews` に `selected_agent_roles` を渡す

### `POST /reviews`（Request例）
```json
{
  "prd_text": "...",
  "panel_type": null,
  "selected_agent_roles": ["engineer", "pm"]
}
```

## 5. 移行計画
- まずは既存4ロールのみ公開（既存互換）。
- 追加ロールは TOML/定数とプロンプトが整い次第、`/agents/roles` とプリセットに段階的に露出。
- 後方互換: `selected_agent_roles` 未指定時は全員（4名）。
