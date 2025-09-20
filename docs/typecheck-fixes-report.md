# Typecheck修正レポート

## 概要

CIのtypecheck（mypy --strict）で発生しているエラーの修正作業の詳細レポート

## 実施日時

2025-09-20

## 初期状態のエラー（13件）

```
src/hibikasu_agent/services/mock_service.py:75: error: Redundant cast to "list[Issue]"
src/hibikasu_agent/services/mock_service.py:114: error: Redundant cast to "list[Issue]"
src/hibikasu_agent/services/mock_service.py:130: error: Redundant cast to "list[Issue]"
src/hibikasu_agent/agents/parallel_orchestrator/agent.py:30: error: Unused "type: ignore" comment
src/hibikasu_agent/agents/parallel_orchestrator/agent.py:30: error: Function is missing a type annotation
src/hibikasu_agent/services/providers/adk.py:38: error: Call to untyped function "InMemorySessionService"
src/hibikasu_agent/services/providers/adk.py:136: error: Call to untyped function "InMemorySessionService"
src/hibikasu_agent/services/providers/adk.py:162: error: Missing type parameters for generic type "dict"
src/hibikasu_agent/services/ai_service.py:39: error: Unused "type: ignore" comment
src/hibikasu_agent/services/ai_service.py:50: error: Incompatible types in assignment
src/hibikasu_agent/services/ai_service.py:116: error: Redundant cast to "list[Issue]"
src/hibikasu_agent/services/ai_service.py:168: error: Redundant cast to "list[Issue]"
src/hibikasu_agent/services/ai_service.py:184: error: Redundant cast to "list[Issue]"
```

## 実施した修正

### 1. mock_service.py - 冗長なキャストの削除（完了）

- **問題**: `cast("list[Issue]", session.issues)` が不要
- **原因**: `session.issues` は既に `list[Issue]` 型として定義されている
- **修正内容**:
  - `from typing import cast` のインポートを削除
  - 3箇所の `cast("list[Issue]", session.issues)` を `session.issues` に変更
  - 行番号: 75, 114, 130

### 2. ai_service.py - 冗長なキャストの削除と型エラー修正（完了）

- **問題**:
  - `cast("list[Issue]", sess.issues)` が不要（3箇所）
  - `current: Exception | None` が `BaseException | None` であるべき
  - 未使用の `type: ignore` コメント
- **修正内容**:
  - `from typing import cast` を削除
  - 3箇所の `cast("list[Issue]", sess.issues)` を `sess.issues` に変更（行番号: 116, 168, 184）
  - `current: Exception | None` を `current: BaseException | None` に変更（行番号: 34）
  - `errors = current.errors()  # type: ignore[reportAny]` から `type: ignore` を削除（行番号: 39）

### 3. providers/adk.py - 型アノテーション追加（部分的に完了）

- **問題**:
  - `InMemorySessionService()` の呼び出しが untyped
  - `dict` に型パラメータが不足
  - `int()` 呼び出しで型エラー
- **修正内容**:
  - `InMemorySessionService()` に `# type: ignore[no-untyped-call]` を追加（行番号: 38, 136）
  - `list[dict]` を `list[dict[str, object]]` に変更（行番号: 162）
  - `int(item.get("priority") or 0)` を `int(item.get("priority", 0))` に変更（行番号: 195）

### 4. parallel_orchestrator/agent.py - 型アノテーション修正（進行中）

- **問題**:
  - `_run_async_impl` メソッドの型アノテーションが不適切
  - `InvocationContext` の import が必要
- **修正内容**:
  - 必要なインポートを追加:
    ```python
    from collections.abc import AsyncGenerator
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from google.adk.agents.base_agent import InvocationContext
    ```
  - メソッドシグネチャを修正:
    ```python
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:  # type: ignore[override]
    ```

## 現在の状態のエラー（3件）

```
src/hibikasu_agent/agents/parallel_orchestrator/agent.py:12: error: Module "google.adk.agents.base_agent" does not explicitly export attribute "InvocationContext"
src/hibikasu_agent/agents/parallel_orchestrator/agent.py:36: error: Unused "type: ignore" comment
src/hibikasu_agent/services/providers/adk.py:195: error: No overload variant of "int" matches argument type "object"
```

## 残っている問題と対策

### 1. InvocationContext のインポートエラー

- **問題**: `google.adk.agents.base_agent` から `InvocationContext` が正しくエクスポートされていない
- **対策案**:
  1. 別のモジュールから `InvocationContext` をインポート
  2. `Any` 型を使用して回避
  3. プロトコルを定義して使用

### 2. int() の型エラー

- **問題**: `item.get("priority", 0)` が `object` 型として推論される
- **対策案**:
  1. 明示的な型アサーション
  2. 型ガードの実装
  3. デフォルト値の処理を変更

### 3. 未使用の type: ignore コメント

- **問題**: `type: ignore[override]` が不要になった可能性
- **対策案**: コメントを削除して再確認

## `TYPE_CHECKING` と `__init__` 使用について

### 現在のコードで使用している手法

現在のコードでは、型チェック時のみのインポートを行うために `TYPE_CHECKING` を使用している：

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.adk.agents.base_agent import InvocationContext
```

### 問題点と推奨アプローチ

この手法には以下の問題がある：

1. **実行時の型情報欠如**: 実行時に型情報が利用できない
2. **デバッグの困難さ**: ランタイムエラーが発生しやすい
3. **IDE支援の制限**: 一部のIDEで適切な補完やチェックが行われない可能性

### 推奨される解決策

#### 1. 適切な型アノテーション（推奨）

```python
from typing import Any
from collections.abc import AsyncGenerator

async def _run_async_impl(self, ctx: Any) -> AsyncGenerator[Event, None]:
```

#### 2. プロトコルの定義（より型安全）

```python
from typing import Protocol

class InvocationContextProtocol(Protocol):
    # 必要なメソッドやプロパティを定義
    pass

async def _run_async_impl(self, ctx: InvocationContextProtocol) -> AsyncGenerator[Event, None]:
```

#### 3. 条件付きインポート（現在の手法）

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from some.module import RealType
else:
    RealType = object  # ランタイム用のダミー型
```

### 修正方針

本プロジェクトでは、以下の方針で修正を進める：

1. **Google ADKライブラリの型定義不足**: `Any` 型を使用して回避
2. **明確な型が存在する場合**: 適切な型アノテーションを使用
3. **型安全性とコード保守性のバランス**: 過度に複雑にならない範囲で型安全性を確保

## 次のステップ

1. **InvocationContext の問題解決**
   - `Any` 型を使用して実用的な解決を図る
   - 必要に応じてプロトコル定義を検討

2. **int() の型エラー修正**
   - 明示的な型アサーションまたは型ガードを実装

3. **最終確認**
   - すべての修正後に `make typecheck` で確認
   - CIが通ることを確認

## 注意事項

- `type: ignore` の使用は最小限に抑える
- 冗長な実装になっても型安全性を優先
- Google ADK のライブラリは型定義が不完全な可能性があるため、必要に応じて `type: ignore` を使用
- `TYPE_CHECKING` の過度な使用は避け、実行時の型安全性も考慮する

## コマンド

```bash
# typecheck実行
make typecheck

# または直接実行
uv run mypy src/ --strict
```
