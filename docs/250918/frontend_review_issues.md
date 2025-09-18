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
