# API仕様書

フロントエンドとバックエンド間の通信規約（コントラクト）を以下に定義する。

---

## 共通データモデル

APIの各エンドポイントで共通して利用されるデータ構造。

### `Issue` モデル
単一の指摘事項（論点）を表すオブジェクト。

```typescript
interface Issue {
  issue_id: string;      // システムが付与する一意のID
  priority: number;      // ユーザーに提示する際の優先順位
  agent_name: string;    // 指摘を生成した、または代表するエージェント名
  agent_avatar: string;  // 表示用のエージェントのアバターアイコンID
  severity: "High" | "Mid" | "Low"; // 指摘の重要度
  comment: string;       // 指摘内容のテキスト
  original_text: string; // 指摘箇所に該当するPRD原文の引用
}
```

### `ReviewSession` モデル
レビューセッション全体の状態を表すオブジェクト。

```typescript
interface ReviewSession {
  status: "processing" | "completed" | "failed" | "not_found";
  issues: Issue[] | null;
}
```

---

## エンドポイント定義

### 1. レビューセッションの開始

ユーザーからPRDテキストを受け取り、AIレビュープロセスをバックグラウンドで開始する。

- **Endpoint:** `POST /reviews`
- **Request Body:**
  ```json
  {
    "prd_text": "ユーザーはダッシュボードの表示項目を自由にカスタマイズできる。",
    "panel_type": "Webサービス"
  }
  ```
- **Response Body (Success):**
  ```json
  {
    "review_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
  }
  ```

---

### 2. レビュー状態と結果の取得

指定したセッションIDの現在の状態（処理中か、完了したか）と、完了している場合はレビュー結果（論点リスト）を取得する。フロントエンドは、`status`が`completed`または`failed`になるまでこのエンドポイントを定期的にポーリングする。

- **Endpoint:** `GET /reviews/{review_id}`
- **Path Parameters:**
  - `review_id` (string): `POST /reviews`で取得したセッションID。
- **Request Body:** なし
- **Response Body (Processing):**
  ```json
  {
    "status": "processing",
    "issues": null
  }
  ```
- **Response Body (Completed):**
  ```json
  {
    "status": "completed",
    "issues": [
      {
        "issue_id": "ISSUE-001",
        "priority": 1,
        "agent_name": "エンジニアAI",
        "agent_avatar": "icon-engineer.png",
        "severity": "High",
        "comment": "カスタマイズ項目の保存ロジックにN+1問題が発生するリスクがあります...",
        "original_text": "ユーザーはダッシュボードの表示項目を自由にカスタマイズし、その設定を保存できる。"
      }
    ]
  }
  ```

---

### 3. 対話による論点の深掘り

特定の論点について、担当AIと対話を行う。

- **Endpoint:** `POST /reviews/{review_id}/issues/{issue_id}/dialog`
- **Path Parameters:**
  - `review_id` (string): 現在のセッションID。
  - `issue_id` (string): 対話したい論点のID。
- **Request Body:**
  ```json
  {
    "question_text": "N+1問題について、もう少し具体的に教えてください。"
  }
  ```
- **Response Body (Success):**
  ```json
  {
    "response_text": "50個以上の項目を一度に保存した場合、DBへのリクエストが大量に発生し、サーバーの応答時間が5秒以上かかる可能性があります..."
  }
  ```

---

### 4. 修正案の提案

特定の論点について、AIに具体的なPRDの修正案を要求する。

- **Endpoint:** `POST /reviews/{review_id}/issues/{issue_id}/suggest`
- **Path Parameters:**
  - `review_id` (string): 現在のセッションID。
  - `issue_id` (string): 修正案が欲しい論点のID。
- **Request Body:** なし
- **Response Body (Success):**
  ```json
  {
    "suggested_text": "PRDの要件に以下を追記することを推奨します。「ユーザー体験を損なわないため、一度に保存できる項目は最大100個までとする。」",
    "target_text": "ユーザーはダッシュボードの表示項目を自由にカスタマイズし、その設定を保存できる。"
  }
  ```

---

### 5. 修正案の適用

AIが提案した修正案を、バックエンドで管理しているPRD原文に適用する（MVPではPRD更新はシミュレートされ、成功ステータスのみを返す）。

- **Endpoint:** `POST /reviews/{review_id}/issues/{issue_id}/apply_suggestion`
- **Path Parameters:**
  - `review_id` (string): 現在のセッションID。
  - `issue_id` (string): 適用したい修正案を持つ論点のID。
- **Request Body:** なし
- **Response Body (Success):**
  ```json
  {
    "status": "success"
  }
  ```
