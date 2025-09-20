# リファクタリング TODOリスト

`refactor_targets.md` で特定された各リファクタリング項目を、依存関係とレビュー指摘を考慮して3つのステップに再構成したものです。
この順序で進めることで、コンフリクトや破壊的変更を避け、安全にリファクタリングを進めます。

---
---

## ステップ1: 基盤となる構造変更

**目的:** 主要なクラス (`AiService`, `ADKService`) の責務を明確化し、設定情報を一元管理することで、以降のリファクタリングの安定した土台を築く。

### 1-1. ADKService の責務分割とユーティリティ化
**背景:** `ADKService` が Span 計算、Issue 変換、セッション生成、Runner 実行など多くの責務を抱えている。
**対象ファイル:** `src/hibikasu_agent/services/providers/adk.py`

- [x] `src/hibikasu_agent/utils/` ディレクトリに `span_calculator.py` を新規作成し、`_normalize_text`, `_calculate_span` などの Span 計算関連のメソッド群を純粋な関数として移管する。
- [x] `ADKService` から Span 計算ロジックを削除し、新しい `span_calculator` モジュールを呼び出すように変更する。
- [x] ADK のセッションと `Runner` の初期化処理（`InMemorySessionService` の生成、ID生成、`Runner` のインスタンス化）を、`AdkSessionFactory` のような専用のファクトリクラスまたは関数に切り出す。
- [x] `run_review_async` 内の `Runner` 初期化処理を、この新しいファクトリの呼び出しに置き換える。
- [x] `_create_api_issue` メソッドの責務を見直し、辞書から `ApiIssue` オブジェクトへの変換ロジックを、`api/mappers.py` のような専用のマッパーモジュールに分離することを検討する。

### 1-2. レビューセッション管理と ADK 実行の分離
**背景:** `AiService` がセッションのインメモリ管理と ADK の非同期プロセス実行を両方担っており、責務が密結合している。
**対象ファイル:** `src/hibikasu_agent/services/ai_service.py`

- [x] レビューセッション (`_reviews`辞書) の状態管理に特化した `ReviewSessionStore` クラスを新規に作成する。
- [x] `new_review_session`, `get_review_session`, `find_issue`, `update_issue_status` 等のセッション操作メソッドを `AiService` から `ReviewSessionStore` に移管する。
- [x] `AiService` は `ReviewSessionStore` のインスタンスを保持し、セッション操作はそちらに委譲する形に変更する。
- [x] ADK の実行ロジック (`kickoff_review` の中身) をカプセル化する `AdkReviewRunner` クラスまたはモジュールを新規に作成する。
- [x] `AdkReviewRunner` に、`async def run(...)` のような純粋な非同期メソッドを実装し、`asyncio.run` の呼び出しを `AiService` から分離する。
- [x] `AiService` の `kickoff_review` は、`AdkReviewRunner` の `run` メソッドを呼び出す（またはバックグラウンドタスクとして起動する）責務のみを持つようにする。

### 1-3. エージェント生成ロジックの段階的な移行
**背景:** `create_specialist_from_role` 等のファクトリが複数の箇所で利用されており、一斉な変更は破壊的変更につながる。
**対象ファイル:** `src/hibikasu_agent/agents/**/*.py`

- **フェーズ1: 新しい設定ベースのファクトリを導入**
    - [x] `constants/agents.py` に、専門家エージェントの設定を定義するデータ構造（例: `dataclass` のリスト）を追加する。
    - [x] 新しい設定リストを元にエージェント群を生成するファクトリ関数 `create_specialists_from_config(config, model)` を実装する。
- **フェーズ2: オーケストレーターの移行**
    - [x] `parallel_orchestrator/agent.py` での `create_specialist_from_role`, `create_role_agents` の呼び出しを、新しい `create_specialists_from_config` に置き換える。
- **フェーズ3: 個別エージェントの移行**
    - [x] `agents/{engineer,ux_designer,qa_tester,pm}/agent.py` で `create_specialist_from_role` を利用している箇所を、新しい設定ベースのファクトリを利用するように変更するか、各エージェントが直接自身のインスタンスを生成するように変更する。
- **フェーズ4 (最終):**
    - [x] すべての呼び出し元が移行されたことを確認した上で、古い `create_specialist_from_role` と `create_role_agents` を非推奨（deprecated）とし、最終的に削除する。

---
---

## ステップ2: 新しい構造内でのロジック改善

**目的:** ステップ1で確立した新しいクラス・モジュール構造の上で、各機能の内部ロジックを改善し、堅牢性と可読性を向上させる。

### 2-1. 集約ツールの責務分離と可読性向上
**背景:** `aggregate_final_issues` が多くの責務を持ち、複雑性が高い。
**対象ファイル:** `src/hibikasu_agent/agents/parallel_orchestrator/tools.py`

- [x] (ステップ1-3完了後) `aggregate_final_issues` 内の逐次的な state 読み込み処理を、 `constants/agents.py` の設定リストをループして動的に読み込むようにリファクタリングする。
- [x] 指摘事項の優先度付けロジックを、独立したヘルパー関数 `_calculate_issue_priorities(...)` に切り出す。
- [x] `aggregate_final_issues` の戻り値を、`dict` ではなく型付けされた `FinalIssuesResponse` オブジェクトに変更し、シリアライズは呼び出し元の `FinalIssuesAggregatorAgent` で行うように責務を分離する。

### 2-2. 堅牢なイベントベース進捗管理への移行
**背景:** ADK イベントの `author` 文字列への依存は脆弱である。
**対象ファイル:** (リファクタリング後の `AdkReviewRunner` または関連クラス)

- [x] `_handle_adk_event` (または相当するメソッド) が `event.author` をパースする代わりに `event.actions.state_delta` を監視するように変更する。
- [x] `constants/agents.py` の `*_ISSUES_STATE_KEY` を参照し、`state_delta` にキーが出現したら対応するエージェントが完了したと判断するロジックを実装する。

### 2-3. プロンプトの安全な外部ファイル化
**背景:** プロンプトのハードコードはメンテナンス性が低く、パッケージングの考慮が必要。
**対象ファイル:** `pyproject.toml`, `src/hibikasu_agent/services/providers/adk.py`, `src/hibikasu_agent/agents/parallel_orchestrator/agent.py`

- [ ] `pyproject.toml` の `[tool.poetry.packages]` または `[tool.poetry.include]` に、テンプレートファイルが含まれるように設定を追加する。（例: `include = "hibikasu_agent/templates"`）
- [ ] `src/hibikasu_agent/` 配下に `templates` ディレクトリを作成し、`dialog_prompt.jinja2` 等のプロンプトファイルを配置する。
- [ ] `importlib.resources` を利用してテンプレートファイルを読み込むロジックを実装し、ハードコードされたプロンプトを置き換える。Jinja2 等のライブラリ追加も検討する。

### 2-4. サービス層からの表示ロジックの分離
**背景:** サービス層に UI 表示目的のデータ整形ロジックが混在している。
**対象ファイル:** (リファクタリング後の `ReviewSessionStore`), `adk.py` (または `mappers.py`)

- [ ] 新しい `ReviewSessionStore` 内のサマリー生成ロジックから、ステータスキーを日本語ラベルに変換する `label_map` を削除する。
- [ ] `ApiIssue` への変換ロジックから、サマリーをヒューリスティックに生成・切り詰めする処理を削除する。表示上の加工はフロントエンドの責務とする。

### 2-5. ユニットテストの拡充
- [x] `aggregate_final_issues`、`ReviewSessionStore`、`AdkReviewRunner`、`_handle_adk_event` の単体テストを追加し、出力の整合性を検証する。

---
---

## ステップ3: 全体的なクリーンアップ

**目的:** 他のすべてのリファクタリングが完了した後、プロジェクト全体の import 文の整合性をとり、コードベースを最終的にクリーンな状態にする。

### 3-1. `__init__.py` ファサードの廃止とインポートパスの統一
**背景:** プロジェクトの方針として、`__init__.py` によるファサードを設けず、importパスは実体のファイルパスと一致させることを優先する。
**対象ファイル:** プロジェクト全体

- [x] `hibikasu_agent/api/schemas/__init__.py` や `hibikasu_agent/schemas/__init__.py` など、再エクスポートを行っている `__init__.py` をリストアップする。
- [x] `grep` 等で、これらのファサード経由でインポートしている箇所（例: `from hibikasu_agent.api.schemas import Issue`）をすべて特定する。
- [x] 特定したインポート文を、すべて実体のファイルパスからの直接インポート（例: `from hibikasu_agent.api.schemas.reviews import Issue`）に修正する。
- [x] プロジェクト内のすべての参照を更新した後、対象の `__init__.py` の中身を空にするか、ファイルを削除する。
- [ ] **補足:** この作業は機械的な置換が多くなるため、IDEの検索・置換機能を活用して効率的に進める。
