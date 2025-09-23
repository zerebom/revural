# フロントエンド変更案（UI/フロー/ストア・更新）

対象: Next.js App Router + Zustand（`frontend/`）

本書はコード変更を含みません。UI仕様と配線方針を明確化します。

## 1. 体験フロー（同一画面MVP）
1) PRD入力 → 2) 体制プリセット選択 → 3) メンバー選択（プロフィールカード） → 4) レビュー開始 → 5) 結果
- 下部に「体制」「メンバー」ブロックを追加（`PrdInputForm` 内に統合）
- アクションバーに「選択中: n名」＋「選択したn名でレビューを開始」

## 2. プロフィールカード方針（UIのみ）
- 表記: 名前は日本語、bioは約80文字・1文。タグは最大3（超過は +n）
- 構成: Avatar/イニシャル + 名前 + 選択中Badge → 1行bio → タグ（2-3）
- 実装: 既存 shadcn/ui（`Card`, `Avatar`, `Badge`, `Tooltip`, `ScrollArea`）

## 3. API呼び出し
- `api.startReview(prd_text, panel_type?, selected_agent_roles?)` に拡張（第3引数）
- `api.getReview` は既存。`expectedAgents`/`completedAgents` は display_name へ変換表示
- `GET /agents/roles`/`GET /agent-presets` を初回ロードで取得

## 4. ストア（Zustand）
- 追加: `selectedRoles: string[]`
- Actions: `setSelectedRoles(roles: string[])`, `toggleRole(role: string)`、既存 `setIssues`, `reset`
- 型ファイル（`frontend/lib/types.ts`）の追加変更は不要。ロール一覧はローカル型 or 匿名型で扱う。

## 5. コンポーネント
- `TeamPresetSelect`: プリセット選択＋適用ボタン（`onApply(roles)`）
- `MemberSelectGrid`: ロール一覧カードのトグル（選択数表示・全選択/クリア任意）
- `ProfileCard`: プロフィール中心カード（日本語名/80字bio/タグ）
- 統合先: `PrdInputForm.tsx` に2コンポーネントを組み込み、開始ボタン文言を切替

## 6. バリデーション/UX
- 選択0名: 開始ボタン無効＋ヘルパー表示
- 選択上限: 4名（超過時はトースト）
- 既知修正:
  - `frontend/app/reviews/[id]/page.tsx` の `React.use(params)` 問題を修正
  - 結果0件時に `issues=[]` と `expandedIssueId=null` を確実に反映

## 7. ローディング/空状態/エラー
- 役割/プリセット取得: スケルトン → エラー時は再試行
- レビュー実行中: `LoadingSpinner` に display_name を表示
- 空結果時: ステート初期化（`expandedIssueId=null`）

## 8. テスト
- API呼び出し: `startReview` に `selected_agent_roles` が渡る
- UI相互作用: プリセット適用→トグル→開始の操作が意図通り
- 0名/上限超過/空結果/エラーの各分岐表示

## 9. ロールアウト
- フィーチャーフラグで新UIを段階露出。既存体験と併存可能
