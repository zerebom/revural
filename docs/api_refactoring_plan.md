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
-   [ ] `src/hibikasu_agent/core/` ディレクトリを作成する。
-   [ ] `src/hibikasu_agent/core/config.py` を作成する。
-   [ ] `config.py` 内に、`pydantic_settings.BaseSettings` を継承した `Settings` クラスを定義する。
    -   `CORS_ALLOW_ORIGINS` や `HIBIKASU_LOG_LEVEL` などの環境変数をフィールドとして定義する。
-   [ ] `main.py` にあったCORSオリジンを決定するロジック (`_allowed_origins_from_env` など) を `Settings` クラス内に移動または `config.py` 内の関数として再実装する。
-   [ ] `main.py` が `core.config` から設定を読み込むように修正する。

#### ✅ 成功の確認方法
1.  **[振る舞い]** リファクタリング後も、APIサーバーが正常に起動し、CORSエラーなどが発生せず、これまで通りフロントエンドからアクセスできることを確認する。
2.  **[コード]** `main.py` から `_allowed_origins_from_env` や `_allowed_origin_regex_from_env` といった関数がなくなり、CORSミドルウェアの設定が `config.settings.CORS_ALLOW_ORIGINS` のようにシンプルになっていることを確認する。

---

### ステップ2: サービス層の再構築 (Business Logic Layer)

**目的:** ビジネスロジックを担うサービス層をAPI層から独立させ、インターフェースを定義する。

-   [ ] `src/hibikasu_agent/services/` ディレクトリを作成する。
-   [ ] 既存の `src/hibikasu_agent/api/services/` ディレクトリの中身 (`ai.py`, `base.py`, `mock.py`) を `src/hibikasu_agent/services/` に移動する。
-   [ ] `services/base.py` を修正し、`ReviewServiceBase` のような抽象基底クラス (ABC) を定義する。
    -   `new_review_session`, `get_review_session`, `find_issue` などのメソッドシグネチャを `@abstractmethod` で定義する。
-   [ ] `services/ai.py` と `services/mock.py` のクラス名をそれぞれ `AiService`, `MockService` に変更し、`ReviewServiceBase` を継承させる。
-   [ ] 古い `src/hibikasu_agent/api/services/` ディレクトリを削除する。

---

### ステップ3: 依存性注入の導入 (Decoupling)

**目的:** FastAPIのDI（依存性注入）システムを利用して、ルーターとサービス層を疎結合にする。

-   [ ] `src/hibikasu_agent/api/dependencies.py` を作成する。
-   [ ] `dependencies.py` に `get_service` 関数を定義する。
    -   この関数は `core.config` の設定を読み、`AiService` または `MockService` のインスタンスを返す責務を持つ。
-   [ ] `api/routers/reviews.py` の各エンドポイントを修正する。
    -   `get_service()` の直接呼び出しをやめる。
    -   関数の引数に `service: ReviewServiceBase = Depends(get_service)` を追加し、サービスインスタンスを注入する形に変更する。
-   [ ] `main.py` から `install_default_review_impl` の呼び出しを削除する（DIに責務が移譲されるため）。

---

### ステップ4: スキーマの分割 (Data Models)

**目的:** 機能ごとにスキーマ定義ファイルを分割し、関連性を明確にする。

-   [ ] `src/hibikasu_agent/api/schemas/` ディレクトリを作成する。
-   [ ] `src/hibikasu_agent/api/schemas/reviews.py` を作成する。
-   [ ] 既存の `src/hibikasu_agent/api/schemas.py` から、`reviews` に関連する全てのPydanticモデル (`ReviewRequest`, `Issue`, `StatusResponse`など) を `api/schemas/reviews.py` に移動する。
-   [ ] `api/routers/reviews.py` のスキーマのインポート元を `api.schemas` から `api.schemas.reviews` に修正する。
-   [ ] `src/hibikasu_agent/api/schemas.py` が空になれば削除する。

---

### ステップ5: クリーンアップ

**目的:** `main.py` を最終的に整理し、責務をアプリケーションの起動のみに限定する。

-   [ ] `main.py` の `lifespan` 関数内にあるロギング設定ロジックを、`hibikasu_agent.utils.logging_config` に移動し、`lifespan` から呼び出すだけにする。
-   [ ] `main.py` から不要になったインポート文を削除する。
-   [ ] 全体の修正後、APIが正常に動作することをテストで確認する。
