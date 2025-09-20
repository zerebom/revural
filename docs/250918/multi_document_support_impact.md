# マルチドキュメントレビュー対応 – 影響サマリ

現在「PRD」を前提にしているコードおよびユーザー向け資産を洗い出し、任意の文書タイプへ拡張する際に必要となる修正ポイントをまとめました。

## 1. プラットフォーム全体での概念整理
- **ネーミングとコピー:** README、プロンプト、UIコピー、ログなどが文書を「PRD」と断定している。中立的な呼称（例: `source_document`）と、文書タイプごとのラベル付けが必要。
- **パネル選択:** `panel_type` は現在 PRD向けのパネルを想定。複数の文書タイプに対応するには、(a) `document_type` や `review_focus` を受け取る新フィールド、(b) タイプからエージェント構成を決めるオーケストレーションロジック、(c) フロントエンドの入力UIが求められる。

## 2. バックエンド / API
- **リクエストスキーマ:** `src/hibikasu_agent/api/schemas/reviews.py`
  - `ReviewRequest.prd_text`、`ReviewSession.prd_text`、`StatusResponse.prd_text` をリネームまたは拡張し（例: `document_text`、`document_type`）、既存クライアントとの後方互換を維持する。
  - ドキュメンテーションやバリデーションで「PRD」を前提にしている箇所（IssueSpan の説明等）を一般化。
- **ルーター:** `src/hibikasu_agent/api/routers/reviews.py`
  - POST ハンドラが `prd_len` をログに出し `req.prd_text` を使用しているため、新しいフィールド名に合わせて修正。
  - `issue_suggest` の返却文は PRD 固有の定型文になっており差し替えが必要。
- **サービスランタイム:**
  - `src/hibikasu_agent/services/ai_service.py` と `services/models.py` が `prd_text` を保持。フィールド名、進捗文言、エラーメッセージなどを汎用化する。
  - `kickoff_review` で `adk_service.run_review_async(prd_text=...)` を呼び出しているほか、進捗メッセージが PRD 固定。
- **ADK プロバイダ:** `src/hibikasu_agent/services/providers/adk.py`
  - メソッドシグネチャ（`_find_simple_span`、`_calculate_span`、`run_review_async`）とコメントが PRD 前提。命名・説明の全面見直しが必要。
  - `default_review_agents` が固定配列のため、文書タイプごとに異なるエージェントセットを選択できる仕組みが求められる。
- **スペシャリスト連携:**
  - `src/hibikasu_agent/agents/parallel_orchestrator/agent.py` と `agents/specialist.py` の説明文・指示文に「PRD」が埋め込まれている。文書タイプをパラメータ化するかニュートラルな表現へ変更する。
  - `prompts/agents.toml` も役割別プロンプトが同様の前提。テンプレート化またはタイプ別バリアントの整備が必要。
- **スキーマ/モデル:** `src/hibikasu_agent/schemas/models.py`
  - `Issue.original_text` の説明、`FinalIssue` のドキュメントコメント、`ReviewSession.prd_text` などが PRD 固定。
- **テスト:** `tests/api/test_*` が `prd_text` を含むペイロードを送信。新フィールド名への更新と文書タイプ分岐のテスト追加が必要。

## 3. フロントエンド（Next.js）
- **API クライアント:** `frontend/lib/api.ts` が `{ prd_text }` をシリアライズし、レスポンスも `prd_text` を受け取っている。
- **グローバル型とストア:** `frontend/lib/types.ts`、`frontend/store/useReviewStore.ts` が `prd_text` を公開しているため、フィールド名変更と各コンポーネントへの伝播が必要。
- **エントリーフォーム:** `frontend/components/PrdInputForm.tsx` のフィールド名、プレースホルダ、ボタン文言が PRD 向け。文書タイプ選択を含む汎用フォームへの置き換えを検討。
- **文書ビューア:**
  - `frontend/components/PrdTextView.tsx` が `prdText` を想定し、空状態メッセージに「PRDテキスト」と記載。
  - `ReviewPage.tsx` の見出しや説明文に「PRDドキュメント」。
  - `IssueListView` / `IssueAccordionItem` にも PRD という文言が存在する可能性があるため確認の上修正。
- **ローディング UI:** `frontend/components/LoadingSpinner.tsx` のメッセージが「専門家がPRDを解析しています」になっている。
- **スタイル／コピー:** `frontend/app/globals.css` 自体への影響は薄いが、クラス名等で PRD を参照していないか確認。

## 4. プロダクトコピーとドキュメント
- `README.md`、`docs/250906/prd.md`、`docs/250906/usm.md`、`docs/250914/user_story_map.md` など、プロダクト資料の多くが PRD 前提。マルチドキュメント対応を説明する改訂または追補が必要。

## 5. 追加で検討すべき作業軸
- **文書タイプのタクソノミ:** 受け入れる文書種別（enum）の定義と、標準エージェントパネルへのマッピングを策定。
- **移行戦略:** 既存の PRD クライアントを維持するため、移行期間に `prd_text` と `document_text` を並行受付するなどの互換策を検討。
- **プロンプトのパラメータ化:** 文書タイプ情報をプロンプトへ渡す方法（文字列テンプレート vs. `panel_type` からの動的差し込み）を決定。
- **UX バリデーション:** 文書タイプを取得しつつユーザー体験を損なわない導線を設計。自動推定＋ユーザー確認などの選択肢を評価。
- **テレメトリ調整:** PRD をキーにしている分析項目は、新しい文書タイプも識別できるよう更新。

## 6. 想定工数メモ
- バックエンドのスキーマ／サービス改修: 中規模（API 層・サービス層・テストに波及）。
- プロンプト／エージェント再設計: 中〜大（レビュー品質劣化を防ぐ検証が必要）。
- フロントエンドのリネームと UI 調整: 中規模（ストア、型、フォーム、ビューア、コピー修正）。
- 新しい選択UX（今実装する場合）: 大規模 — 別スコープでの検討が妥当。

上記の観点を踏まえて優先度付けを行い、段階的なリリース計画を組むことで、マルチドキュメント対応への移行をスムーズに進められます。
