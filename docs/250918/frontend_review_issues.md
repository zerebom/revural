# フロントエンド実装の現状課題メモ（2025-09-18）

## 概要
先日の実装レビューで洗い出した主要な課題を整理する。優先度の高い順に記載し、対応の方向性メモも添える。

## 課題一覧
1. **Next.jsの`params`展開でクラッシュ**（Blocker）
   - 対象: `frontend/app/reviews/[id]/page.tsx:11`
   - 内容: クライアントコンポーネント内で `React.use(params)` を呼び出しており、React 18 では `React.use` が未実装のため即座に実行時エラー。
   - 方針: `params` はサーバー側で解決するか、`use(params)` 互換の App Router API を正しく利用して書き換える。

2. **レビュー完了時に指摘が空だと前回データが残存**（Major）
   - 対象: `frontend/app/reviews/[id]/page.tsx:32`
   - 内容: `data.issues.length > 0` のときだけ Zustand ストアを更新しているため、指摘が 0 件の場合に前回レビューの `issues` / `expandedIssueId` が表示され続ける。
   - 方針: `issues` が空でも常に `setIssues` と `setExpandedIssueId(null)` を走らせる。

3. **レビュー状態のリセットが未使用**（Major）
   - 対象: `frontend/store/useReviewStore.ts:23`
   - 内容: `reset()` が定義されているものの、ページ遷移や新規レビュー開始時に呼ばれていない。結果として表示モードや展開中の指摘が次のセッションへ引き継がれる。
   - 方針: レビュー開始前やトップページへ戻るタイミングで `reset()` を呼ぶ。

4. **サマリーページが再取得しない**（Major）
   - 対象: `frontend/components/SummaryPage.tsx:88`
   - 内容: `useSWR` を一度呼ぶだけで、サマリー生成待ち状態をフォローできない。ステータスが `processing` のままならページを開き直さない限り更新されない。
   - 方針: ポーリング間隔を設ける、もしくは `mutate()` をトリガーする仕組みを入れる。

5. **エクスポートボタンがダミー実装**（Major）
   - 対象: `frontend/components/ReviewPage.tsx:53`
   - 内容: UI 上は使用可能に見えるが内部処理は `console.warn("未実装")`。ユーザー体験として好ましくない。
   - 方針: 機能が未提供ならボタンを非表示/無効化する。将来的には `SummaryPage` の Markdown エクスポートと同等の処理を共有化する。

6. **ハイライト位置の信頼性が低い**（Minor）
   - 対象: `frontend/components/PrdTextView.tsx:33`
   - 内容: スパンが欠損している場合 `original_text` の最初の一致位置を単純検索している。文章内に同一テキストが複数回現れると誤った箇所をハイライトし、重複スパンは `cursor` ロジックで切り捨てられる。
   - 方針: バックエンドでスパン情報を必須化するか、マッチ位置を複数考慮するロジックに改良する。

7. **API ベース URL のデフォルトが危険**（Minor）
   - 対象: `frontend/lib/api.ts:3`
   - 内容: `NEXT_PUBLIC_API_BASE_URL` 未設定時に `http://localhost:8000` を使用。ステージング/本番で環境変数設定を忘れるとブラウザからローカルホストへリクエストして即座に失敗する。
   - 方針: 相対パス利用やビルド時バリデーションで早期に気付けるようにする。

## 次のアクション候補
- Blocker を最優先で修正し、レビュー詳細ページの描画を正常化。
- Zustand ストアのリセット導線と空配列対応をセットで行い、セッション切り替え時の表示崩れを防ぐ。
- サマリーページのポーリング有無を決定し、必要なら `useSWR` の `refreshInterval` を導入。
- 仕様上未提供のボタン/機能は UI から排除するか明示的な disabled 表示を行う。
- `IssueAccordionItem.tsx` / `SummaryPage.tsx` / `legacy/IssueCard.tsx` では `shortenOriginalText` を必ず経由して元テキストを表示し、長文ハイライトがそのまま出ないようにする（2025-09-19 対応済み、要レビュー）。

## ハイライト不具合の原因調査メモ（2025-09-18）
- **症状**: 指摘が複数あるのに `<mark>` が 1 つしか描画されないケースがあり、特に span が無い指摘で顕著。
- **原因1（バックエンド）**: `src/hibikasu_agent/schemas/models.py:35` の `IssueItem` に `span` フィールドがなく、スペシャリストが返した span 情報がパース時に捨てられている。その結果、最終レスポンスの `span` は常に `None` から再計算される。
- **原因2（バックエンド再計算）**: `ADKService._calculate_span()` は空白除去のみで一致判定しており、エージェントが原文を軽く整形した場合（箇条書きを削除、語尾調整など）に `original_text` と PRD が一致せず、span 生成に失敗する。
- **原因3（フロントエンド）**: `frontend/components/PrdTextView.tsx:30` のフォールバック検索は `prdText.indexOf(issue.original_text)` の最初の一致だけを使用し、`cursor` ロジックで重複位置を打ち切るため、同じ抜粋を指す指摘が複数あると最初の 1 件のみハイライトされる。

### 対応アイデア
1. バックエンドのスキーマ (`IssueItem`, `FinalIssue`, API `Issue`) に `span` を追加し、スペシャリストの出力をそのまま保持。`ADKService` 側では提供された span を優先し、従来の `_calculate_span()` はフォールバックとして残す。
2. `_calculate_span()` のマッチ精度を向上させる（NFKC 正規化、ケース変換、複数候補探索など）ことで軽微な表記ゆれでも span を復元できるようにする。
3. フロントエンド側でフォールバック検索を改良し、同一テキストが複数回登場する場合でも未使用の位置を順番に割り当て、`cursor` 判定で後続の `<mark>` を破棄しないようにする。
