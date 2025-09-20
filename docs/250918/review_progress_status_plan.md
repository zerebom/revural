# AIレビュー進行状況表示改善計画
n

## 背景
- 現行UIでは`processing/completed/failed`の3状態のみで、レビュー進行中に何が起きているか伝わらずユーザー体験が弱い。
- バックエンドの`AiService`では`ReviewRuntimeSession.status`しか更新しておらず、中間フェーズの可視化ができない (`src/hibikasu_agent/services/models.py`).
- ADK実行を担う`ADKService.run_review_async`は`Runner.run_async`が返すイベントストリームを捨てており、進捗情報を引き出していない (`src/hibikasu_agent/services/providers/adk.py`).

## 調査結果
- ADKランナー (`.venv/lib/python3.12/site-packages/google/adk/runners.py:245-315`) は非同期ジェネレータで`Event`を順次返す。`Event.author`や`branch`からどのサブエージェントが応答したか判定できる。
- 各イベントは`Event.actions.state_delta`でセッションステート差分を運べる仕組みを持つ (`.venv/lib/python3.12/site-packages/google/adk/events/event_actions.py:45-48`).
- `Event.is_final_response()`で終端イベント（最終レスポンス）と途中イベントを判別可能 (`.venv/lib/python3.12/site-packages/google/adk/events/event.py:93-108`).

## 直近のリグレッション調査 (2025-09-18)

### 500エラーの直接原因
- `aggregate_final_issues` が Pydantic モデル `FinalIssuesResponse` をそのまま返す実装に変更されたが、ADK の `FunctionTool` は戻り値を dict へシリアライズする前提で `types.FunctionResponse` を生成するため、JSON シリアライズできないオブジェクトが返ると `Object of type FinalIssuesResponse is not JSON serializable` が発生し、ADK 側で内部エラーになり API 500 を誘発する。
- 該当箇所: `src/hibikasu_agent/agents/parallel_orchestrator/tools.py:94` で Pydantic インスタンスを返却している。
- ADK の処理フロー: `.venv/lib/python3.12/site-packages/google/adk/flows/llm_flows/functions.py:693` 以降で戻り値を dict 化 (`{'result': function_result}`) しようとする。
- 対処方針: ツールの戻り値は `response.model_dump()` など JSON シリアライズ可能な構造に揃える。`state["final_review_issues"]` へは引き続き dict を格納するため、戻り値だけ明示的に dict / list へ変換すれば互換性を保てる。

### original_text トリミングと span 計算の齟齬
- `_trim_original_text` によって指摘箇所の `original_text` が 160 文字上限で末尾に `...` を付与しており、PRD からそのまま抜粋した文字列でなくなるケースがある。
- span 計算は `ADKService._calculate_span`（`src/hibikasu_agent/services/providers/adk.py:140`）で PRD 内の位置を `original_text` から逆算しているため、末尾が `...` に置換されると一致判定に失敗し、UI ハイライトがずれるまたは欠落する。
- 対処方針: 表示用と照合用のテキストを分ける、あるいはトリミング時に PRD 内の実際の切り出しを保持して `span` 計算に支障を与えないようにする（例: 末尾を単純に切り捨て、表示時のみ `...` を挿入する）。

## 実装方針
1. **ReviewRuntimeSessionの拡張**
   - 追加フィールド案：
     - `phase: Literal[...]`（例: `"specialists_running"`, `"aggregating"`, `"post_processing"`）
     - `progress: float`（0.0〜1.0）
     - `eta_seconds: int | None`
     - `phase_message: str | None`
     - `expected_agents: list[str]`：今回のセッションで実行するエージェント名を保持し、進捗や完了判定の基準にする（フロントからの動的構成に対応）。
     - （必要に応じて）`history: list[PhaseLog]`

2. **ADKイベント処理の導入**
   - `ADKService.run_review_async`で`async for event in runner.run_async(...)`を処理し、イベントごとに`AiService`へ通知。
   - `event.actions.state_delta`があれば`ReviewRuntimeSession`に反映。
   - `event.author`や`branch`からスペシャリスト完了を検知して`phase`/`progress`を更新。
   - `event.is_final_response()`が真になった時点で最終結果を構築。
   - `AiService`側に`update_progress(review_id, phase, progress, message)`のようなヘルパーを追加。

3. **フロントエンド連携**
   - `/api/reviews/{id}`レスポンスに`phase`, `progress`, `phaseMessage`, `etaSeconds`を追加し、`frontend/lib/types.ts`・`frontend/lib/api.ts`を更新。
   - `ReviewPage.tsx`や`LoadingSpinner.tsx`でフェーズ別メッセージ/アニメーションを表示。
   - 初期はポーリング短縮で対応しつつ、将来的にSSE/WebSocketを検討。

4. **エージェント側の補助**
   - `src/hibikasu_agent/agents/parallel_orchestrator/agent.py`にコールバックを仕込み、スペシャリスト終了時に`state_delta`を吐く（例: `{"phase": "specialist_done", "agent_name": ...}`）。

5. **エラーハンドリング**
   - イベント処理中の例外は`ReviewRuntimeSession.status = "failed"`へ遷移、`phase_message`でユーザーへの説明を更新。
   - 失敗コピーもポジティブなものを準備。

## バックエンドTODO
- `src/hibikasu_agent/schemas/models.py`：`ReviewRuntimeSession`拡張（必要なら`PhaseLog`追加）。
- `src/hibikasu_agent/services/ai_service.py`：新フィールドの初期化とレスポンス拡張、進捗更新ヘルパーの実装。
- `src/hibikasu_agent/services/providers/adk.py`：イベントループ処理を実装し、進行状況を`AiService`へ伝搬。最終イベント処理を明確化。
- エージェント定義へ`state_delta`発火のための改修（必要に応じて）。

## フロントエンドTODO
- `frontend/lib/types.ts`/`frontend/lib/api.ts`の型拡張。
- `frontend/components/ReviewPage.tsx`：フェーズ表示・期待感のある演出追加。
- `frontend/components/LoadingSpinner.tsx`：段階別スピナー・メッセージ差し替え機構を整備。
- `IssueListView.tsx`などのローディング表示調整。

## リスクと検討事項
- イベント粒度が十分でない場合、エージェント側で追加の`state_delta`を構築する必要あり。
- ETA推定は暫定値のため、初期リリースでは控えめな表現に留める。
- SSE/WebSocket導入時はインフラ設定やタイムアウトを確認。

## 実装アプローチの段階的推奨

1. **エージェント完了ステータスの導入（最小構成）**
   - `Runner`のイベントから`event.author`や`branch`をもとに各エージェントの完了を検知し、`ReviewRuntimeSession`に`completed_agents: set[str]`といったフィールドを追加して記録。
   - 進捗バーは `len(completed_agents) / total_agents` のシンプルな比率で算出する。エージェント数が増減してもリストを差し替えるだけで対応できる。
   - フロントエンドではエージェントごとの完了チェックリストと粗い進捗バーを表示し、ユーザーに「誰が動いているか」を見せる。

2. **フェーズ／コピー／ETAなどの拡張（本計画のフル版）**
   - 上記ステータス運用で得た知見を踏まえ、`phase`や`phase_message`、ヒューリスティックな`eta_seconds`を追加。
   - 必要に応じてエージェントへ`state_delta`を発火させ、より細かな情報（例: 集約中の進捗）をUIへ届ける。
   - SSE/WebSocketなどリアルタイム配信チャネルが必要になった段階で導入する。

この段階的アプローチにより、まずはシンプルな改善で運用を安定させ、のちに表現力豊かな進捗演出へスムーズに拡張できる。

### 2025-09-19 メモ
- 現状は ADK イベントの `author` / `branch` 解析に失敗した場合はログのみ残して進捗を進めない暫定実装。次ステップとして、各スペシャリストが完了時に `state_delta` へ `{"completed_agent": "engineer_specialist"}` を書き出すようにエージェント定義を拡張するタスクを切ること。

エージェント構成がユーザー操作で変化する場合は、セッション生成時に受け取ったリストを`expected_agents`へ保存し、イベント処理側ではこのリストを基準に`completed_agents`や進捗率を算出する。


## 推奨ロードマップ
1. バックエンドで進捗フィールドとイベント処理を実装し、ポーリングAPIで段階表示ができる状態を作る。
2. フロントでフェーズ別UIを整備し、ユーザー体験を改善。
3. その後、エージェントからの詳細`state_delta`やETA改善、リアルタイム配信（SSE/WebSocket）を検討。

ユーザーが「何を待っているのか」「どこまで進んだのか」を感じ取れるレビュー体験を目指し、段階的に適用する。
