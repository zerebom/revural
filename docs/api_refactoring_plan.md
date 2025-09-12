# APIリファクタリング計画

## 1. はじめに

このドキュメントは、`src/hibikasu_agent/api/` 配下のコードベースを、よりメンテナンス性が高く、責務が明確に分離された構成にリファクタリングするための計画を定義する。

現在のコードベースは、FastAPIアプリケーションとして機能しているものの、以下の課題を抱えている。

-   `main.py` に設定、ロギング、アプリケーション起動のロジックが混在している。
-   ルーター (`routers/`) にビジネスロジックが一部含まれている。
-   スキーマ定義が一つのファイルに集約されており、機能分割されていない。
-   サービス層の依存関係が不明確である。

本計画に沿ってリファクタリングを進めることで、これらの課題を解決し、将来の機能追加やテストを容易にすることを目指す。

## 2. 理想的なディレクトリ構成

リファクタリング後の理想的なディレクトリ構成は以下の通り。

```
src/hibikasu_agent/
├── api/
│   ├── __init__.py
│   ├── main.py             # FastAPIの起動とルーター登録のみ
│   ├── dependencies.py     # DI (依存性注入) に関連する関数
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── reviews.py      # ルーティング定義に専念
│   │
│   └── schemas/
│       ├── __init__.py
│       └── reviews.py      # reviews関連スキーマ
│
├── core/
│   └── config.py           # 環境変数、CORS設定などを管理
│
└── services/
    ├── __init__.py
    ├── base.py             # サービスインターフェースを定義 (ABC)
    ├── ai_service.py       # AIを使ったサービス実装
    └── mock_service.py     # モックサービス実装
```

## 3. リファクタリングのステップとToDoリスト

以下のステップ順で進めることを推奨する。各ステップは独立しており、影響範囲を限定しながら段階的に実施できる。

---

### ステップ1: 設定の分離 (Foundation)

**目的:** `main.py` から設定関連のロジックを`core/config.py`に分離し、設定を一元管理する。

#### As-Is (現状)
- CORSの許可オリジンリストやロギングレベルといった設定値が、`os.getenv()` を通じて `main.py` 内で直接参照・解決されている。
- 設定値を取得するための補助的な関数 (`_allowed_origins_from_env` など) が `main.py` 内に定義されている。
- 設定の全体像を把握するには `main.py` を読み解く必要がある。

#### To-Be (理想形)
- `src/hibikasu_agent/core/config.py` に `pydantic-settings` を利用した `Settings` クラスが定義され、アプリケーション全体の設定値が属性として一元管理されている。
- `main.py` は `Settings` クラスのインスタンスをインポートして利用するだけで、設定値の解決ロジックからは解放される。
- 環境変数の追加や変更は `config.py` の修正のみで完結する。

#### ToDoリスト
-   [x] `src/hibikasu_agent/core/` ディレクトリを作成する。
-   [x] `src/hibikasu_agent/core/config.py` を作成する。
-   [x] `config.py` 内に、`pydantic_settings.BaseSettings` を継承した `Settings` クラスを定義する。
    -   `CORS_ALLOW_ORIGINS` や `HIBIKASU_LOG_LEVEL` などの環境変数をフィールドとして定義する。
-   [x] `main.py` にあったCORSオリジンを決定するロジック (`_allowed_origins_from_env` など) を `Settings` クラス内に移動または `config.py` 内の関数として再実装する。
-   [x] `main.py` が `core.config` から設定を読み込むように修正する。

#### ✅ 成功の確認方法
1.  **[振る舞い]** リファクタリング後も、APIサーバーが正常に起動し、CORSエラーなどが発生せず、これまで通りフロントエンドからアクセスできることを確認する。
2.  **[コード]** `main.py` から `_allowed_origins_from_env` や `_allowed_origin_regex_from_env` といった関数がなくなり、CORSミドルウェアの設定が `config.settings.CORS_ALLOW_ORIGINS` のようにシンプルになっていることを確認する。

---

### ステップ2: サービス層の再構築 (Business Logic Layer)

**目的:** ビジネスロジックを担うサービス層をAPI層から独立させ、インターフェースを定義する。

#### As-Is (現状)
- `src/hibikasu_agent/api/services/` と `src/hibikasu_agent/services/` という2つの `services` ディレクトリが混在し、責務が曖昧。
- `api/services/base.py` のインターフェース定義 (`ReviewService`) が `TypedDict` であり、実装の継承による規約になっていない。
- `api/services/mock.py` が存在するものの、未使用で「トマソン」化している。
- ビジネスロジック (`runtime.py`) がAPI層のすぐ下 (`api/services`) をインポートしており、レイヤー構造が逆転しかけている。

#### To-Be (理想形)
- `services` ディレクトリは `src/hibikasu_agent/services/` に統一され、FastAPIなどのWebフレームワークから独立した純粋なビジネスロジック層となる。
- `services/base.py` に、`abc` モジュールを使った抽象基底クラス `AbstractReviewService` が定義され、実装すべきメソッドが `@abstractmethod` で明確化される。
- `services/ai_service.py` (旧`runtime.py`) と `services/mock_service.py` (旧`mock.py`) が `AbstractReviewService` を継承し、同じインターフェースを持つことが保証される。
- 古い `src/hibikasu_agent/api/services/` ディレクトリは完全に削除される。

#### ToDoリスト
-   [x] `src/hibikasu_agent/services/` の下に `base.py`, `ai_service.py`, `mock_service.py` を作成する。
-   [x] `services/base.py` に `AbstractReviewService(ABC)` を定義し、`@abstractmethod` を使ってサービスメソッドのインターフェースを宣言する。
    -   `new_review_session`, `get_review_session`, `find_issue`, `kickoff_compute` などの主要メソッドを定義する。
-   [x] `services/ai_service.py` に `AiReviewService(AbstractReviewService)` クラスを作成し、既存の `services/runtime.py` と `api/services/ai.py` のロジックを移植・統合する。
-   [x] `services/mock_service.py` に `MockReviewService(AbstractReviewService)` クラスを作成し、既存の `api/services/mock.py` のロジックを移植する。
-   [x] ルーター (`api/routers/reviews.py`) など、サービスをインポートしている箇所のパスを新しい `services` モジュール (`hibikasu_agent.services.ai_service` など) に修正する。
-   [x] アプリケーションが新しいサービス層で正常に動作することを確認する。
-   [x] 不要になった `src/hibikasu_agent/api/services/` ディレクトリを削除する。
-   [x] 不要になった `src/hibikasu_agent/services/runtime.py` を削除する。

#### ✅ 成功の確認方法
1. **[振る舞い]** リファクタリング後も、APIサーバーが正常に起動し、`POST /reviews` などの主要な機能が以前と同様に動作することを確認する。
2. **[コード]** `src/hibikasu_agent/api/services/` ディレクトリが存在しないことを確認する。`AiReviewService` と `MockReviewService` が `AbstractReviewService` を継承しており、メソッドシグネチャが一致していることを確認する。
3. **[テスト]** `MockReviewService` を対象とした新しい単体テストが追加され、パスすること。具体的には、セッションの作成 (`new`) → 状態取得 (`get`) → 指摘事項の検索 (`find`) という一連の流れが正しく機能することを確認するテスト。

---

### ステップ3: 依存性注入の導入 (Decoupling)

**目的:** FastAPIのDI（依存性注入）システムを利用して、ルーターとサービス層を疎結合にする。これにより、テスト時にモック実装へ差し替えることが極めて容易になる。

#### As-Is (現状)
- ルーター (`api/routers/reviews.py`) が `AiService` のような具体的な実装クラスを直接インポートし、エンドポイント関数内でインスタンス化している。
- どのサービス実装（AIかモックか）を使うかが、ルーターのコードにハードコードされている。
- `main.py` に `install_default_review_impl(app)` という古いDIの仕組みが残っている。

#### To-Be (理想形)
- `api/dependencies.py` に、設定に応じて `AiService` または `MockService` のインスタンスを返す `get_service` DI関数が定義される。
- ルーターは、具象クラスをインポートせず、`AbstractReviewService` インターフェースと `get_service` DI関数のみに依存する。
- 各エンドポイントは、`Depends(get_service)` を通じて、FastAPIから自動的にサービスインスタンスが引数として**注入**される。
- ルーターは注入された `service` オブジェクトの実装を意識することなく、インターフェースで定義されたメソッドのみを呼び出す。
- `main.py` から古いDIの仕組みである `install_default_review_impl(app)` の呼び出しは削除される。

#### ToDoリスト
-   [x] `src/hibikasu_agent/api/dependencies.py` を作成する。
-   [x] `dependencies.py` に `get_service` 関数を定義する。この関数は、設定に応じて `AiService` または `MockService` のインスタンスを返す責務を持つ。（初期実装では常に `AiService` を返す形でよい）
-   [x] `api/routers/reviews.py` を修正する。
    -   [x] `fastapi` から `Depends` をインポートする。
    -   [x] `AiService` のような具象クラスのインポートを削除し、`AbstractReviewService` と `get_service` をインポートする。
    -   [x] 各エンドポイント関数の引数に `service: AbstractReviewService = Depends(get_service)` を追加し、サービスインスタンスを注入する形に変更する。
-   [x] `main.py` から `install_default_review_impl` のインポートと呼び出しを削除する。

#### ✅ 成功の確認方法
1.  **[振る舞い]** リファクタリング後も、APIサーバーが正常に起動し、これまで通り `/reviews` エンドポイントが機能することを確認する。
2.  **[コード]** `api/routers/reviews.py` に `AiService` や `MockService` への直接のインポート文が存在しないことを確認する。エンドポイントのシグネチャに `Depends(get_service)` が含まれていることを確認する。
3.  **[テスト]** （発展）FastAPIの `app.dependency_overrides` を使って、テスト時に `get_service` を `MockService` を返す関数に差し替えることができるか確認する。

---

### ステップ3.5: テストのリファクタリング (Decoupling Tests)

**目的**: DI導入のメリットを最大限に活かし、API層のテストをサービス層から分離する。これにより、高速で安定し、関心事が明確なユニットテストを実現する。

#### As-Is (現状)
- APIのテスト (`tests/api/test_reviews_endpoints.py`) が、`TestClient` を通じてアプリケーション全体を起動し、デフォルトの `AiService` に依存してしまっている。
- テストが遅く、不安定になる可能性があり、API層だけの振る舞いを検証することが難しい。

#### To-Be (理想形)
- APIのテスト実行時には、FastAPIの `app.dependency_overrides` を使って、`get_service` 依存性が常に `MockService` を返すように上書きされる。
- テストは `MockService` の高速かつ予測可能なレスポンスを前提に書かれ、API層のロジック（リクエストの検証、適切なサービスの呼び出し、レスポンスの整形など）のみを検証することに集中できる。
- `AiService` のテストは、独立したサービスクラスのユニットテストとして（必要であれば）別途実装される。

#### ToDoリスト
-   [x] `tests/api/conftest.py` を追加し、`app.dependency_overrides` を設定/解除するフィクスチャを提供する。
    -   [x] `override_get_service` 相当（`mock_service_override`）を定義し、常に `MockService` を返す。
    -   [x] `client` フィクスチャ（MockService適用）、`client_ai_mode` フィクスチャ（DI未上書き）を提供する。
-   [x] `tests/api/test_reviews_endpoints.py` を修正する。
    -   [x] `client` フィクスチャを使用する形に変更し、アサーションはモックのダミーデータに基づく検証にする。
    -   [x] AIモデルの不安定な挙動に依存する前提を排し、確実なアサーションへ修正。

---

### ステップ4: スキーマの分割 (Data Models)

**目的:** 機能ごとにスキーマ定義ファイルを分割し、関連性を明確にする。

-   [x] `src/hibikasu_agent/api/schemas/` ディレクトリを作成する。
-   [x] `src/hibikasu_agent/api/schemas/reviews.py` を作成する。
-   [x] 既存の `src/hibikasu_agent/api/schemas.py` から、`reviews` に関連する全てのPydanticモデル (`ReviewRequest`, `Issue`, `StatusResponse`など) を `api/schemas/reviews.py` に移動する。
-   [x] `src/hibikasu_agent/api/schemas/__init__.py` で `reviews` の型を再エクスポートし、既存の `from hibikasu_agent.api.schemas import ...` が引き続き機能するようにする。（必要に応じて `api.schemas.reviews` へ切替可能）
-   [x] `src/hibikasu_agent/api/schemas.py` を削除する。

---

### ステップ5: クリーンアップ

**目的:** `main.py` を最終的に整理し、責務をアプリケーションの起動のみに限定する。

-   [ ] **ロギング設定のリファクタリング:**
    -   [ ] `main.py` の `lifespan` 関数内にあるロギング設定ロジックを、`hibikasu_agent.utils.logging_config` に移動し、`lifespan` から呼び出すだけにする。
        -   [ ] `utils/logging_config.py` に `setup_application_logging(level: str)` のような関数を新設する。
        -   [ ] `main.py` の `lifespan` 内にあったハンドラ設定などのロジックを `setup_application_logging` に移植する。
        -   [ ] `main.py` の `lifespan` は `setup_application_logging(settings.hibikasu_log_level)` を呼び出すだけの実装にする。
-   [ ] `main.py` から不要になったインポート文 (`logging`, `sys` など) を削除する。
-   [ ] 全体の修正後、APIが正常に動作することをテストで確認する。

---

### ステップ6: サービス内部実装の改善 (Implementation Details)

**目的 (Why):** これまでのステップで整えたクラスの「構造」を基盤に、個々のメソッドの「内部実装」を改善する。これにより、グローバルな状態への依存をなくし、各クラスを自己完結させ、コードの可読性、安全性、そしてテスト容易性を最終的なゴールへと引き上げる。

---

#### 1. サービスインターフェースの見直し (What & Why)

- **What**: `kickoff_compute` メソッドを `AbstractReviewService` インターフェースから削除する。その責務を `new_review_session` メソッドに統合し、`start_review_process` のような単一の非同期メソッドへと再設計する。
- **Why**: 現在の設計では、「レビューの受付」と「レビューの実行開始」という、本来一体であるべき責務が2つのメソッドに分離してしまっている。これらを一つに統合することで、サービスを利用する側（ルーター）のコードがシンプルになり、インターフェースがより直感的になる。

- **ToDo**:
    -   [ ] `AbstractReviewService` の `kickoff_compute` と `new_review_session` を、`async def start_review_process(...)` という単一の抽象メソッドに置き換える。
    -   [ ] `AiService` と `MockService` が、この新しい非同期メソッドを正しく実装するように修正する。
    -   [ ] `api/routers/reviews.py` が、新しい `start_review_process` メソッドを `await` 付きで呼び出すように修正する。

---

#### 2. `AiService` の自己完結化 (What & Why)

- **What**: `runtime.py` が持っているロジックと状態（インメモリキャッシュ）を、すべて `AiService` クラスのメソッドとインスタンス変数として移植する。最終的に `runtime.py` を削除する。
- **Why**: 現在の `AiService` は `runtime.py` の薄いラッパーであり、ロジックが外部モジュールに分散している。また、`runtime.py` はグローバル変数 (`reviews_in_memory`, `_review_impl_holder`) を多用しており、テストの分離や将来の拡張を困難にしている。ロジックと状態を `AiService` クラス内にカプセル化することで、クラスが自己完結し、オブジェクト指向の恩恵を最大限に享受できる。

- **ToDo**:
    -   [ ] `AiService` の `__init__` で、`self._reviews_in_memory = {}` のようにインスタンス変数を初期化する。
    -   [ ] `runtime.py` の `new_review_session`, `get_review_session`, `find_issue`, `kickoff_compute` のロジックを、対応する `AiService` のメソッド内に移植し、グローバル変数ではなく `self._reviews_in_memory` を参照するように書き換える。
    -   [ ] `_review_impl_holder` や `set_review_impl` といった古いDIの仕組みを完全に撤廃し、`AiService` が `adk.py` のレビューパイプラインを直接インポートして呼び出すように変更する。
    -   [ ] `AiService` が `runtime.py` に依存しなくなったことを確認し、`runtime.py` ファイルを削除する。

---

#### 3. データ構造の厳密化 (What & Why)

- **What**: レビューセッションの状態を保持するデータ構造を、現在の `dict[str, Any]` から、Pydanticモデル (`ReviewSession`) に変更する。
- **Why**: `dict[str, Any]` は、どのようなキーが存在し、その値がどの型であるべきかを全く保証しない。これは、typoによる `KeyError` や、予期せぬ `TypeError` の温床となる。Pydanticモデルを導入することで、データ構造がコードとして文書化され、静的解析やIDEの補完が効くようになり、安全性と開発体験が劇的に向上する。

- **ToDo**:
    -   [ ] `schemas/reviews.py`（あるいは `schemas/common.py`）に、`status`, `issues`, `prd_text` などのフィールドを持つ `ReviewSession(BaseModel)` クラスを定義する。
    -   [ ] `AiService` と `MockService` のインメモリキャッシュの型ヒントを `dict[str, ReviewSession]` に変更する。
    -   [ ] `get_review_session` メソッドの戻り値の型ヒントを `dict[str, Any]` から `ReviewSession` に変更し、ルーター側もそれに合わせて修正する。

---

-   [ ] **(その他)**
    -   [ ] リファクタリングの過程で見つかった、その他の内部実装に関する改善点をここに追記する。
