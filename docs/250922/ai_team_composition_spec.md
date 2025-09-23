# AIレビューチーム編成 仕様（統合版・最新版）

この文書は 250922 配下の各ドキュメント（overview/backend/frontend/ui_IA/presets/profile_spec/user_data/implementation_tasks）を統合し、議論反映済みの最新版です。コード変更は本ドキュメントでは行いません。

## 1. 決定事項（結論）
- **体験の核**: “観点”ではなく“人を指名して編成”
- **画面構成**: MVPは「PRD入力＋体制選択＋メンバー選択」を同一画面で完結
- **カード様式**: プロフィール中心（大きめアバター、役割名、短いbio、タグ2-3）
- **表記**: 名前は日本語表記推奨、bioは約80文字・1文、タグは最大3個（超過は+n）
- **選択人数**: 1〜4名（推奨3〜4）。0名は開始不可
- **API**: `POST /reviews` に `selected_agent_roles?: string[]` を任意で受け付ける（未指定は従来4名）。`GET /agents/roles` で表示用ロール一覧
- **実装範囲**: まずは既存4ロールのみ公開（将来ロールはUI/定数のみ先行準備）

## 2. 画面情報設計（IA・同一画面MVP）
- 上部: PRD入力テキストエリア（既存）
- 体制プリセット: `Select` + 「プリセットを適用」ボタン（選択ロール置換）
- メンバー選択: プロフィールカードのグリッド（3〜4列、カード高さ固定）
- アクションバー: 「選択中: n名」＋「選択したn名でレビューを開始」
- アクセシビリティ: カードは `button`/`aria-pressed`、フォーカスリング

補助UI（任意）
- タグフィルタ（chips）、検索、スケルトン、空/エラー時の再試行

## 3. プロフィールカード仕様（UI用メタ）
最小スキーマ（コード変更なし・UI側マージ）
- `id: string`（例: "engineer"）
- `name: string`（日本語推奨。例: "エンジニア スペシャリスト"）
- `role_label: string`（例: "エンジニアAI"）
- `avatarUrl?: string`
- `bio?: string`（約80文字・1文）
- `tags?: string[]`（最大3）

JSON例
```json
{
  "id": "copywriter",
  "name": "レオ・マルティネス",
  "role_label": "コピーライターAI",
  "avatarUrl": "/avatars/leo_martinez.png",
  "bio": "ブランドボイスを保ちながら、心に響くマイクロコピーを提案します。UXと成果に直結する言葉選びを支援。",
  "tags": ["#UXライティング", "#マイクロコピー", "#CTA改善"]
}
```

表示ルール
- ヘッダー: アバター/イニシャル + name + 「選択中」Badge
- サブ: bio（最大2行、全文はTooltip可）
- フッター: tags 2-3個 + 「+n」

## 4. API（仕様のみ・非破壊）
- `POST /reviews`
  - Request
    ```json
    {
      "prd_text": "...",
      "panel_type": null,
      "selected_agent_roles": ["engineer", "pm"]
    }
    ```
  - Response
    ```json
    { "review_id": "7f2b9b6e-..." }
    ```
- `GET /reviews/{review_id}`（既存）
  - Response（例）
    ```json
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
  - 表示名はUIで `agent_key -> display_name` 変換
- `GET /agents/roles`
  - Response（例）
    ```json
    [
      {"role": "engineer", "display_name": "Engineer Specialist", "description": "バックエンドエンジニアの専門的観点からPRDをレビュー"},
      {"role": "ux_designer", "display_name": "UX Designer Specialist", "description": "UXデザイナーの専門的観点からPRDをレビュー"},
      {"role": "qa_tester", "display_name": "QA Tester Specialist", "description": "QAテスターの専門的観点からPRDをレビュー"},
      {"role": "pm", "display_name": "PM Specialist", "description": "プロダクトマネージャーの専門的観点からPRDをレビュー"}
    ]
    ```
- （任意）`GET /agent-presets`
  - Response（例）
    ```json
    [
      {"key": "prd_review", "name": "PRDレビュー", "roles": ["engineer", "ux_designer", "qa_tester", "pm"]}
    ]
    ```

## 5. バリデーション/制約
- クライアント
  - 選択0名は開始不可（ボタン無効化＋ヘルパー表示）
  - 選択上限は4名。超過時はトースト/文言で通知
  - 重複選択は不可（トグル制）
- サーバー（受信時）
  - 未指定→既定4ロール
  - 不正ロールは無視（有効なロールが1つ以上あれば採用、0なら既定）
  - 許容数超過は先頭4件に丸め（403にしない）

## 6. UX状態（詳細）
- 初回ロード: 役割一覧/プリセット取得中はスケルトン
- 体制適用: 「プリセットを適用」で `selectedRoles` を置換しカードに反映
- エラー: 取得失敗時はメッセージ＋再試行
- レビュー中: `LoadingSpinner` に display_name ベースで進捗表示
- 結果0件: issuesを空配列で反映、`expandedIssueId=null` に初期化

## 7. ストア形（説明用・型は変更しない）
```ts
// 説明用ダイアグラム（実コードは既存のまま）
interface ReviewUIState {
  selectedRoles: string[];                 // 新規: 選択ロール
  reviewId: string | null;                 // 既存
  prdText: string;                         // 既存
  issues: Issue[];                         // 既存
  expandedIssueId: string | null;          // 既存
}
```
- アクション（例）: `setSelectedRoles`, `toggleRole`, 既存の `setIssues`, `reset`

## 8. コンポーネント配線（UI）
- `PrdInputForm`
  - 下部に `TeamPresetSelect`（props: `presets`, `onApply(roles)`）
  - `MemberSelectGrid`（props: `roles`, `selected`, `onToggle`）
  - 「選択したn名でレビューを開始」→ `api.startReview(prd, panel, selectedRoles)`
- `LoadingSpinner`
  - `expectedAgents`/`completedAgents` を display_name に変換して表示

## 9. 非機能/制限
- 同時エージェント上限: 4
- 既定モデル: `gemini-2.5-flash`（ADK環境変数で変更可）
- タイムアウト/リトライ: 既存のADK実装に準拠（本仕様では変更しない）

## 10. ロールアウト/互換
- フィーチャーフラグでUI露出を切替（既存体験は維持）
- `selected_agent_roles` 未指定でも従来通り動作
- 既存リンク/ブックマークは不変

## 11. テスト計画（要点）
- API
  - `POST /reviews` にロールを付与→ポーリング→ `expected_agents` が選択分に限定
  - 不正ロール混在時のフォールバック
- フロント
  - プリセット適用→トグル→開始の操作系
  - 0名/上限超過/0件結果/エラー系のUI
- E2E
  - PRD→engineer+pm選択→レビュー→完了

## 12. 開発タスク（サマリ）
- UI: `TeamPresetSelect`/`MemberSelectGrid`/`ProfileCard` を統合し `PrdInputForm` に組み込み
- API: `ReviewRequest.selected_agent_roles` の受け取り、`GET /agents/roles` 実装（定数）
- 変換: `agent_key -> display_name` のUI表示

## 13. 未決事項（要確認）
- 上限4名は確定か（3〜5の範囲で調整余地）
- プリセットの外部公開（URLクエリ `?preset=prd_review` の自動適用）
- 将来ロール（legal/security/copywriter）の公開時期

---
本仕様は「同一画面で“人を指名して編成する”体験」を最小実装で成立させるための最新版です。以降の変更は本ファイルのみ更新します。
