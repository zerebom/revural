# 実装タスク一覧（AIレビューチーム編成・更新）

## 0. 前提
- 既存コードは `selected_agents` の内部受け渡し経路が通っている（サービス層〜ADK）。
- 不足は API入力（`POST /reviews` の第3引数）と UI/ストアの選択機能。

### ✅ **Phase 1 完了** (t-wada式TDD実装)
API基盤でエージェント選択を受け付ける機能が完成。全テスト通過、後方互換性維持。

## 1. バックエンド
- [x] `api/schemas/reviews.py` に `selected_agent_roles: list[str] | None` 追加 ✅ **完了**
- [x] `api/routers/reviews.py` `start_review` で `selected_agent_roles` を `new_review_session(..., selected_agents=...)` へ渡す ✅ **完了**
- [x] `services/base.py` `AbstractReviewService` の抽象メソッド更新 ✅ **完了**
- [x] `MockService` で `selected_agents` パラメータをサポート ✅ **完了**
- [ ] `GET /agents/roles` 追加（`SPECIALIST_DEFINITIONS` から生成）
- [ ] `GET /agent-presets` 追加（サーバー定数）
- [ ] ロギングに `selected_agent_roles` を含める（任意）
- [x] 単体テスト追加（API/サービス） ✅ **完了**
  - [x] `POST /reviews` に選択を付与しても 200 ✅ **完了**
  - [x] 後方互換性（`selected_agent_roles` 未指定でも動作） ✅ **完了**
  - [x] APIスキーマの正常パース ✅ **完了**
  - [ ] ポーリング結果の `expected_agents` が選択分に限定
  - [ ] 不正ロール混在時のフォールバック確認、上限制御

## 2. フロントエンド
- [ ] `frontend/lib/api.ts` `startReview` 第3引数 `selected_agent_roles?: string[] | null` に対応
- [ ] Zustand: `useReviewStore`
  - [ ] `selectedRoles: string[]` を追加
  - [ ] `setSelectedRoles(roles: string[])` / `toggleRole(role: string)` を追加
  - [ ] `reset()` が `selectedRoles` も初期化
- [ ] UI: 新規コンポーネント
  - [ ] `components/team/TeamPresetSelect.tsx`
  - [ ] `components/team/MemberSelectGrid.tsx`
  - （任意）`components/team/ProfileCard.tsx` を活用
- [ ] `PrdInputForm.tsx`
  - [ ] 上記2コンポーネントを統合
  - [ ] ボタン文言を「選択した◯人でレビューを開始」に変更
  - [ ] `startReview(prd, panel, selectedRoles)` で起動
- [ ] 既知不具合の修正
  - [ ] `/app/reviews/[id]/page.tsx` の `React.use(params)` 問題修正
  - [ ] 指摘0件時の `issues`/`expandedIssueId` 初期化

備考: `frontend/lib/types.ts` の型追加は必須ではない（ローカル型で可）。

## 3. プロンプト/ロール（任意）
- [ ] 将来ロール用のセクションを `prompts/agents.toml` に追記（空でも可）
- [ ] 公開時は `constants/agents.py` に `SpecialistDefinition` を追加

## 4. QA/テスト
- [ ] API: 新規エンドポイントのAPITests
- [ ] FE: プリセット選択→メンバー編集→開始の操作テスト
- [ ] E2E: 代表シナリオ
  - PRD入力→プリセット`PRDレビュー`→engineer/pmに絞る→開始→結果に engineer/pm のみが `expectedAgents` に含まれる

## 5. 表示・文言ガイド
- [ ] 名前は日本語、bioは約80文字・1文、タグは最大3（UI内ルール）
- [ ] 表示名は `AGENT_DISPLAY_NAMES` をUI側で適用
- [ ] ロール説明（`review_description`）はカードに表示（存在すれば）

## 6. フィーチャーフラグ/ロールアウト
- [ ] 新UIをフラグ配下で露出（既存体験と併存）

## 7. Definition of Done
- `POST /reviews` に選択ロールを渡せば、選択メンバーのみで並列レビューが走る
- 1画面で、プリセット取得→メンバー選択→開始が完結
- ポーリング中/完了画面に、選択メンバーの表示名が自然に表示
- 指摘0件/失敗時の状態遷移が破綻しない
