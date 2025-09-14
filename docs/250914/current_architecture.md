# SpecCheckアプリケーション 現状アーキテクチャ (2025/09/14)

## 概要

SpecCheckは、製品要求仕様書（PRD）をAIエージェントチームが多角的にレビューし、仕様の曖昧さや潜在的なリスクを指摘することで、開発の手戻りを防ぐことを目的としたWebアプリケーションである。

## フロントエンド (Next.js)

### 主要技術スタック

- フレームワーク: Next.js (App Router)
- UIコンポーネント: React, shadcn/ui
- 状態管理: Zustand
- データフェッチ: SWR
- フォーム管理: React Hook Form
- スタイリング: Tailwind CSS

### ディレクトリ構成と役割

- `frontend/app/`: ルーティングと各ページのエントリーポイント
  - `/page.tsx`: トップページ。PRD入力フォームを配置。
  - `/reviews/[id]/page.tsx`: レビュー結果表示ページ。
- `frontend/components/`: 再利用可能なUIコンポーネント群
  - `PrdInputForm.tsx`: PRDを入力し、レビューを開始するためのフォーム。
  - `ReviewPage.tsx`: レビュー結果ページのメインレイアウト。
  - `PrdTextView.tsx`: PRDテキストと指摘箇所のハイライト表示。
  - `IssueDetailView.tsx`: 選択された指摘の詳細表示。
  - `IssueCard.tsx`: 個々の指摘内容、担当エージェント、優先度などを表示するカード。
  - `ChatWindow.tsx`: 指摘内容についてAIと対話するためのチャットUI。
  - `SuggestionBox.tsx`: AIによる修正提案の表示と適用を行うUI。
- `frontend/lib/`: APIクライアントや型定義など
  - `api.ts`: バックエンドAPIとの通信ロジック。
  - `types.ts`: APIレスポンスなどの型定義。
- `frontend/store/`: グローバルな状態管理
  - `useReviewStore.ts`: Zustandを用いたストア。レビューID、PRDテキスト、指摘リストなどを管理。

### 処理フロー

1.  **PRD入力**: ユーザーがトップページでPRDテキストを入力し、「専門家レビューを開始」ボタンをクリックする。
2.  **レビュー開始要求**: `PrdInputForm` が `api.startReview` を呼び出し、バックエンドにPRDテキストを送信する。
3.  **ページ遷移**: APIからレビューIDが返却されると、ZustandストアにIDとPRDテキストを保存し、レビュー結果ページ (`/reviews/[レビューID]`) に遷移する。
4.  **結果ポーリング**: レビュー結果ページでは `useSWR` を使用し、`api.getReview` を定期的に呼び出してレビューの進捗状況をポーリングする。
5.  **結果表示**: レビューのステータスが `completed` になると、取得した指摘 (`issues`) データをストアに保存し、画面にレンダリングする。
    -   `PrdTextView` がPRD内の指摘箇所をハイライト表示する。
    -   `IssueDetailView` が選択された指摘の詳細を `IssueCard` を用いて表示する。
6.  **インタラクション**:
    -   ユーザーはハイライトをクリックして、表示する指摘を切り替える。
    -   `IssueCard` 内のタブから「AIと対話する」(`ChatWindow`) または「修正案」(`SuggestionBox`) を選択し、AIとの対話や修正案の適用を行うことができる。

## バックエンド (FastAPI - 推定)

`frontend/lib/api.ts` の内容から、バックエンドは以下のエンドポイントを持つFastAPIアプリケーションであると推定される。

- `POST /reviews`: レビューを新規に開始する。
- `GET /reviews/{review_id}`: 指定されたレビューのステータスと結果を取得する。
- `POST /reviews/{review_id}/issues/{issue_id}/dialog`: 特定の指摘についてAIと対話する。
- `POST /reviews/{review_id}/issues/{issue_id}/suggest`: 修正案を生成する。
- `POST /reviews/{review_id}/issues/{issue_id}/apply_suggestion`: 修正案を適用する。

## 状態管理

- グローバルな状態はZustand (`useReviewStore`) で一元管理されている。
- 管理されている主な状態:
  - `reviewId`: 現在のレビューID
  - `prdText`: レビュー対象のPRDテキスト
  - `issues`: 指摘のリスト
  - `selectedIssueId`: ユーザーが選択中の指摘ID

## 改善点の可能性

- **リアルタイム更新**: 現状のポーリング方式はシンプルだが、WebSocketやServer-Sent Events (SSE) を導入することで、よりリアルタイムな更新が可能になり、UXが向上する可能性がある。
- **コンポーネント分割**: `IssueCard.tsx` が多機能であるため、関心事に応じてさらに小さなコンポーネントに分割する余地があるかもしれない。
- **エラーハンドリング**: APIエラーのハンドリングをより詳細に行い、ユーザーに分かりやすいフィードバックを提供できる可能性がある。
