# フロントエンド変更指示書 (250910)

## 1. 概要

本ドキュメントは、AIレビューツールのユーザー体験を根本的に改善するため、既存のフロントエンド設計 (`docs/0907/next.md`) を変更し、「**PRD原文とAIの指摘がシームレスに連動する、文脈に沿ったインタラクティブなレビュー画面**」を実装するための詳細な指示を定めるものです。

### 1.1 背景と目的

-   **現状の課題**: 指摘がリスト形式で表示されるため、元のPRDのどの部分に関する指摘か分かりにくい（「面倒」というフィードバック）。
-   **目指す体験**: PRD全文を表示し、指摘箇所を直接ハイライトすることで、ユーザーが文脈を失うことなく直感的にレビューを進められるようにする。
-   **目的**: この変更により、ユーザーの認知負荷を下げ、レビュー作業の効率と質を劇的に向上させる。

### 1.2 変更の核心

既存の「指摘事項を1件ずつカードで表示する」アーキテクチャから、「**PRD全文表示を主軸とし、選択されたハイライトに応じて詳細を提示する**」アーキテクチャへと抜本的に変更する。

---

## 2. ディレクトリ構成とコンポーネントの責務変更

### 2.1 新しいディレクトリ構成案

コンポーネントの役割変更に伴い、構成を以下のように見直します。

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                  # 変更なし
│   └── reviews/
│       └── [id]/
│           └── page.tsx          # ReviewPage (旧ReviewFocusView) を表示
├── components/
│   ├── **ReviewPage.tsx**        # (新規/改名) 2カラムレイアウトのメインコンテナ
│   ├── **PrdTextView.tsx**       # (新規) 左ペイン: PRD全文とハイライト表示
│   ├── **IssueDetailView.tsx**   # (新規) 右ペイン: 指摘詳細と対話UI
│   ├── IssueCard.tsx             # IssueDetailView内で使用（役割はほぼ維持）
│   ├── ChatWindow.tsx            # IssueDetailView内で使用
│   ├── PrdInputForm.tsx          # 変更なし
│   └── ... (その他UI部品)
├── lib/
│   ├── api.ts
│   └── **types.ts**              # (要更新) APIの型定義
└── store/
    └── **useReviewStore.ts**     # (要更新) 状態管理ストア
```

### 2.2 主要コンポーネントの新しい責務

-   **`reviews/[id]/page.tsx`**:
    -   `ReviewPage` コンポーネントを呼び出すエントリーポイント。
    -   SWRフック (`useSWR`) を用いて `GET /reviews/[id]` をポーリングし、取得したデータをZustandストアに格納する責務を持つ。

-   **`ReviewPage.tsx` (旧 `ReviewFocusView.tsx` から改名・大幅改修):**
    -   アプリケーションのメインUIとなる、**2カラムレイアウトのコンテナ**。
    -   左ペインに `PrdTextView`、右ペインに `IssueDetailView` を配置する。
    -   Zustandストアから状態（`prdText`, `issues`, `selectedIssueId`など）を受け取り、各子コンポーネントにPropsとして渡す。

-   **`PrdTextView.tsx` (新規):**
    -   **左ペイン**を担当。
    -   Propsで受け取った `prdText` (PRD全文) と `issues` (指摘リスト) を表示する。
    -   `issues` 配列をループし、各 `issue` が持つ**開始・終了インデックス** (`startIndex`, `endIndex`) に基づいて、`prdText` の該当部分を動的にハイライトする。
    -   ハイライト部分はクリック可能とし、クリックされると対応する `issue_id` をZustandストアの `setSelectedIssueId` アクションに通知する。
    -   現在選択中の指摘 (`selectedIssueId`) に対応するハイライトは、スタイルを他と変えて強調表示する。

-   **`IssueDetailView.tsx` (新規):**
    -   **右ペイン**を担当。
    -   Zustandストアから `selectedIssueId` と `issues` を受け取る。
    -   `selectedIssueId` が存在すれば、`issues` の中から該当する指摘オブジェクトを探し出し、`IssueCard` と `ChatWindow` を表示する。
    -   `selectedIssueId` が `null` の場合は、「指摘サマリー」や「ハイライトを選択してください」といった案内を表示する。
    -   (将来機能) 指摘のサマリーリストやフィルタ機能もこのコンポーネントが担う。

---

## 3. 状態管理 (Zustand) のスキーマ変更

`store/useReviewStore.ts` で管理する状態を、新しいUIアーキテクチャに合わせて以下のように変更します。

### 3.1 新しいストアのインターフェース

```typescript
// store/useReviewStore.ts

import { create } from 'zustand';
import { Issue } from '@/lib/types'; // 型定義は後述

interface ReviewState {
  reviewId: string | null;
  prdText: string;
  issues: Issue[];
  selectedIssueId: string | null; // ★変更: currentIssueIndexは廃止
  issueStatuses: Record<string, 'pending' | 'done'>; // (将来機能)

  setReviewId: (id: string) => void;
  setPrdText: (text: string) => void;
  setIssues: (issues: Issue[]) => void;
  setSelectedIssueId: (id: string | null) => void; // ★変更
  setIssueStatus: (id: string, status: 'pending' | 'done') => void; // (将来機能)
}

export const useReviewStore = create<ReviewState>((set) => ({
  reviewId: null,
  prdText: '',
  issues: [],
  selectedIssueId: null, // ★変更: 初期値はnull
  issueStatuses: {},

  setReviewId: (id) => set({ reviewId: id }),
  setPrdText: (text) => set({ prdText: text }),
  setIssues: (issues) => set({ issues }),
  setSelectedIssueId: (id) => set({ selectedIssueId: id }),
  setIssueStatus: (id, status) => set((state) => ({
    issueStatuses: { ...state.issueStatuses, [id]: status },
  })),
}));
```

### 3.2 変更のポイント

-   **`currentIssueIndex: number` を廃止**し、代わりに **`selectedIssueId: string | null` を導入**します。これにより、ユーザーが任意の順番で指摘を選択するノンリニアな操作に対応します。
-   初期状態では何も選択されていない (`null`) ことを表現できるようにします。

---

## 4. APIの型定義の更新

バックエンド改修との連携を確実にするため、フロントエンドの型定義を更新します。

### 4.1 `Issue` 型の拡張

`frontend/lib/types.ts` の `Issue` インターフェースに、ハイライト位置を特定するための `span` プロパティを追加します。

```typescript
// frontend/lib/types.ts

// (ReviewStatus, ReviewStatusResponse は変更なし)

export interface IssueSpan {
  start_index: number;
  end_index: number;
}

export interface Issue {
  issue_id: string;
  priority: number;
  agent_name: string;
  comment: string;
  original_text: string;
  span: IssueSpan; // ★追加: ハイライト位置情報
}
```

### 4.2 バックエンドへの要求事項

この変更に伴い、バックエンドの `GET /reviews/[id]` APIは、各 `Issue` オブジェクト内に `span` というキーで `{ "start_index": number, "end_index": number }` という形式の位置情報を含めて返却する必要があります。**このバックエンド改修が、本フロントエンド改修の前提条件（ブロッカー）となります。**

---

## 5. 実装タスクリストと手順

### ステップ 1: 型定義と状態管理の更新 (先行実装)

1.  **`lib/types.ts` の更新**: 上記の指示に従い、`Issue` インターフェースに `IssueSpan` を追加します。
2.  **`store/useReviewStore.ts` の更新**: 上記の指示に従い、ストアのスキーマを `selectedIssueId` を使う形に更新します。

### ステップ 2: コンポーネントの雛形作成

1.  **ファイル/ディレクトリの作成**:
    -   `ReviewFocusView.tsx` を `ReviewPage.tsx` にリネームします。
    -   `components/PrdTextView.tsx` と `components/IssueDetailView.tsx` を新規作成します。
2.  **`reviews/[id]/page.tsx` の修正**:
    -   `ReviewPage` を呼び出すように修正します。
    -   ポーリングロジックは維持し、取得した `issues` と `prdText` をZustandストアに保存する処理を実装します。

### ステップ 3: 2カラムレイアウトの実装

1.  **`ReviewPage.tsx` の実装**:
    -   `flexbox` や `grid` を用いて、左右2カラムのレイアウトを構築します。
    -   Zustandストアから必要なstateを全て取得し、`PrdTextView` と `IssueDetailView` にそれぞれPropsとして渡します。

### ステップ 4: PRD全文とハイライト表示の実装 (最重要)

1.  **`PrdTextView.tsx` の実装**:
    -   受け取った `prdText` と `issues` をもとに、ハイライト表示を実装します。
    -   **実装方法案**:
        -   `issues` を `start_index` でソートします。
        -   `prdText` を `substring` や `slice` を使って、非ハイライト部分とハイライト部分に分割し、それぞれ `<span>` や `<mark>` タグでラップしたコンポーネントの配列を生成します。
        -   各ハイライト用コンポーネントには `onClick` イベントハンドラを設定し、クリックされたら `useReviewStore.getState().setSelectedIssueId(issue.issue_id)` を呼び出すようにします。
        -   `selectedIssueId` と一致する `issue` のハイライトには、特別なCSSクラスを付与して見た目を変えます。

### ステップ 5: 指摘詳細ビューの実装

1.  **`IssueDetailView.tsx` の実装**:
    -   `useReviewStore` から `selectedIssueId` を購読します。
    -   `selectedIssueId` が変更されたら、表示するべき `issue` を見つけ出し、`IssueCard` に渡して表示を更新します。
    -   `IssueCard` と `ChatWindow` の実装は、`docs/0907/next.md` のセクション7で計画されている `Tabs` を用いた設計を流用・実装します。

### ステップ 6: 全体的なスタイリングと微調整

-   `shadcn/ui` のコンポーネントを全面的に活用し、既存のデザインドキュメントに沿ったスタイリングを適用します。
-   ハイライトの色や、選択中のハイライトのスタイルを定義します。
-   全てのコンポーネントが連携してスムーズに動作することをテスト・確認します。
