# フロントエンド変更案（UI/フロー/型）

対象: Next.js App Router + Zustand（`frontend/`）

## 1. 体験フロー
1) PRD入力 → 2) 体制プリセット選択 → 3) メンバー選択（カードUI） → 4) レビュー開始 → 5) 結果画面

- 2/3 は `PrdInputForm` と同一画面に統合（シンプル） or ステップUI（将来）。
- まずは同一画面下部に「体制」と「メンバー」ブロックを追加する方式で実装。

## 2. API呼び出しの変更
- `api.startReview(prd_text, panel_type?, selected_agent_roles?)` に拡張。
- `frontend/lib/api.ts` の `startReview` を第3引数対応に。

```ts
// 変更案（概略）
startReview: (prd_text: string, panel_type?: string | null, selected_agent_roles?: string[] | null) =>
  http<ReviewStartResponse>("/reviews", {
    method: "POST",
    body: JSON.stringify({ prd_text, panel_type: panel_type ?? null, selected_agent_roles: selected_agent_roles ?? null }),
  }),
```

## 3. UIコンポーネント
- `TeamPresetSelect`: プリセットカード/ラジオ（選択時に `selectedRoles` を置換）。
- `MemberSelectGrid`: ロール一覧をカードで表示し、チェックでオン/オフ。選択数を表示。
- `PrdInputForm`:
  - これらを下部に組み込み、「選択した◯人でレビューを開始」ボタンに置換。
  - `useReviewStore` から `selectedRoles` を参照・更新。

## 4. ストア拡張（Zustand）
- `frontend/store/useReviewStore.ts`
  - 追加: `selectedRoles: string[]`、`setSelectedRoles(roles: string[])`、`toggleRole(role: string)`
  - 画面離脱時 `reset()` で初期化（必要に応じてセッション持続）

```ts
// 追加フィールド例
selectedRoles: [],
setSelectedRoles: (roles) => set({ selectedRoles: roles }),
toggleRole: (role) => set((s) => ({
  selectedRoles: s.selectedRoles.includes(role)
    ? s.selectedRoles.filter((r) => r !== role)
    : [...s.selectedRoles, role],
})),
```

## 5. データ取得
- `GET /agents/roles` を初回マウントで取得し、カード一覧を描画。
- `GET /agent-presets` を読み込んでプリセットの表示/反映。
- プリセット選択時は `setSelectedRoles(preset.roles)` で反映。

## 6. 型の拡張（`frontend/lib/types.ts`）
```ts
export interface AgentRoleInfo {
  role: string;
  display_name: string;
  description: string;
}

export interface ReviewStartRequest {
  prd_text: string;
  panel_type?: string | null;
  selected_agent_roles?: string[] | null; // 追加
}
```

## 7. ローディング/結果画面
- 既存 `LoadingSpinner` の `expectedAgents` は agent_key を表示中。UI側で display_name 変換テーブルを持ち、わかりやすい名称で表示。
- 完了後 `issues` は現行通り。ただし 0 件時のリセット/初期化（`expandedIssueId=null`）を確実にする修正を同時実施。

## 8. バリデーション/UX
- 選択人数が 1〜6 程度に収まるよう UIでガイド（3〜4人を推奨表示）。
- 未選択時は開始ボタンを無効化し、ヘルパーテキスト表示。

## 9. テスト
- `TeamPresetSelect`/`MemberSelectGrid` の相互作用テスト。
- `startReview` 実行時に `selected_agent_roles` が送られることのモックテスト。
- リロード時に選択が正しく初期化/復元（必要に応じて URL パラメータやローカルストレージ）。
