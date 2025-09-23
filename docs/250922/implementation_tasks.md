# 実装タスク一覧（AIレビューチーム編成・更新）

## 0. 前提
- 既存コードは `selected_agents` の内部受け渡し経路が通っている（サービス層〜ADK）。
- 不足は API入力（`POST /reviews` の第3引数）と UI/ストアの選択機能。

### ✅ **Phase 1 完了** (t-wada式TDD実装)
API基盤でエージェント選択を受け付ける機能が完成。全テスト通過、後方互換性維持。

## 1. バックエンド ✅ **PHASE 1 完了**
- [x] `api/schemas/reviews.py` に `selected_agent_roles: list[str] | None` 追加 ✅ **完了**
- [x] `api/routers/reviews.py` `start_review` で `selected_agent_roles` を `new_review_session(..., selected_agents=...)` へ渡す ✅ **完了**
- [x] `services/base.py` `AbstractReviewService` の抽象メソッド更新 ✅ **完了**
- [x] `MockService` で `selected_agents` パラメータをサポート ✅ **完了**
- [x] `GET /agents/roles` 追加（`SPECIALIST_DEFINITIONS` から生成） ✅ **完了** + リッチなプロフィール対応
- [ ] `GET /agent-presets` 追加（サーバー定数） ※別フェーズ
- [ ] ロギングに `selected_agent_roles` を含める（任意） ※別フェーズ

### 🎯 **追加実装**: Single Source of Truth設計
- [x] `SpecialistDefinition` 拡張（role_label, bio, tags, avatar_url）✅ **完了**
- [x] `AgentRole` APIスキーマ追加 ✅ **完了**
- [x] APIレスポンス型安全性向上 ✅ **完了**
- [x] 単体テスト追加（API/サービス） ✅ **完了**
  - [x] `POST /reviews` に選択を付与しても 200 ✅ **完了**
  - [x] 後方互換性（`selected_agent_roles` 未指定でも動作） ✅ **完了**
  - [x] APIスキーマの正常パース ✅ **完了**
  - [ ] ポーリング結果の `expected_agents` が選択分に限定
  - [ ] 不正ロール混在時のフォールバック確認、上限制御

## 2. フロントエンド
### **Phase 2A: API・ストア基盤** ✅ **PHASE 2 完了**
- [x] `frontend/lib/types.ts` に `AgentRole` 型追加 ✅ **完了**
- [x] `frontend/lib/api.ts` 拡張 ✅ **完了**
  - [x] `getAgentRoles(): Promise<AgentRole[]>` 追加 ✅ **完了**
  - [x] `startReview` 第3引数 `selected_agent_roles?: string[]` 対応 ✅ **完了**
- [x] `frontend/store/useReviewStore.ts` 拡張 ✅ **完了**
  - [x] `selectedRoles: string[]` 追加 ✅ **完了**
  - [x] `selectedPreset: string | null` 追加 ✅ **完了**
  - [x] `setSelectedRoles(roles: string[])` / `toggleRole(role: string)` 追加 ✅ **完了**
  - [x] `setSelectedPreset(preset: string | null)` 追加 ✅ **完了**
  - [x] `reset()` 更新（新フィールド対応） ✅ **完了**

### **Phase 2B: UIコンポーネント** ✅ **PHASE 3 完了**
- [x] `components/team/TeamPresetSelect.tsx` ✅ **既存利用可能**
- [x] `components/team/MemberSelectGrid.tsx` **新規作成** ✅ **完了**
  - [x] ProfileCard コンポーネント統合（bio + tags対応） ✅ **完了**
  - [x] レスポンシブグリッドレイアウト（1行3-4枚） ✅ **完了**
  - [x] 選択状態管理とアクセシビリティ対応 ✅ **完了**
- [x] `components/PrdInputForm.tsx` **エージェント選択統合** ✅ **完了**
  - [x] エージェント一覧取得（useEffect + api.getAgentRoles） ✅ **完了**
  - [x] MemberSelectGrid 統合 ✅ **完了**
  - [x] 動的ボタン文言（「選択した○人でレビューを開始」） ✅ **完了**
  - [x] 複合フォーム状態管理とエラーハンドリング ✅ **完了**
  - [ ] TeamPresetSelect 連携 ※Phase 4で実装予定

### **🚀 実装順序（Bottom-Up + 段階的検証）**
**Phase 1: データ基盤（30分）** ✅ **完了**
1. ✅ `types.ts` AgentRole型追加
2. ✅ `api.ts` getAgentRoles() + startReview拡張
3. ✅ API疎通確認

**Phase 2: ストア拡張（20分）** ✅ **完了**
4. ✅ `useReviewStore.ts` 拡張（selectedRoles等）
5. ✅ ストア動作確認

**Phase 3: 最小UIプロト（40分）** ✅ **完了**
6. ✅ `MemberSelectGrid.tsx` 最小版作成
7. ✅ `PrdInputForm.tsx` 一部統合
8. ✅ エンドツーエンド動作確認

**Phase 4: UI強化（60分）** ⬅️ **次の実装フェーズ**
9. ProfileCard本格実装（hero image対応）
10. TeamPresetSelect連携
11. PrdInputForm完全リファクタリング

**Phase 5: 仕上げ（30分）**
12. 既知不具合修正・最終調整
- [ ] 既知不具合の修正
  - [ ] `/app/reviews/[id]/page.tsx` の `React.use(params)` 問題修正
  - [ ] 指摘0件時の `issues`/`expandedIssueId` 初期化

備考: `frontend/lib/types.ts` の型追加は必須ではない（ローカル型で可）。

## 3. プロンプト/ロール（任意）
- [ ] 将来ロール用のセクションを `prompts/agents.toml` に追記（空でも可）
- [ ] 公開時は `constants/agents.py` に `SpecialistDefinition` を追加

## 4. QA/テスト
- [x] API: 新規エンドポイントのAPITests ✅ **完了** (test_agents_roles_endpoint.py)
- [ ] FE: プリセット選択→メンバー編集→開始の操作テスト
- [ ] E2E: 代表シナリオ
  - PRD入力→プリセット`PRDレビュー`→engineer/pmに絞る→開始→結果に engineer/pm のみが `expectedAgents` に含まれる

## 5. 表示・文言ガイド
- [x] 名前は日本語、bioは約80文字・1文、タグは最大3（UI内ルール） ✅ **完了** (SpecialistDefinition拡張)
- [x] 表示名は `AGENT_DISPLAY_NAMES` をUI側で適用 ✅ **完了** (既存機能維持)
- [x] ロール説明（`review_description`）はカードに表示（存在すれば） ✅ **完了** (API提供済み)

## 6. フィーチャーフラグ/ロールアウト
- [ ] 新UIをフラグ配下で露出（既存体験と併存）

## 7. Definition of Done
- ✅ `POST /reviews` に選択ロールを渡せば、選択メンバーのみで並列レビューが走る **完了**
- [ ] 1画面で、プリセット取得→メンバー選択→開始が完結 (フロントエンド実装待ち)
- ✅ ポーリング中/完了画面に、選択メンバーの表示名が自然に表示 **完了** (expected_agents対応済み)
- [ ] 指摘0件/失敗時の状態遷移が破綻しない (フロントエンド実装・テスト待ち)
