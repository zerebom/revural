# Development Patterns and Best Practices

このドキュメントでは、hibikasu-agentプロジェクトで推奨される開発パターンとベストプラクティスを説明します。

## 目次

- [プロジェクト構造](#プロジェクト構造)
- [コーディングパターン](#コーディングパターン)
- [テストパターン](#テストパターン)
- [ロギングパターン](#ロギングパターン)
- [エラーハンドリング](#エラーハンドリング)
- [パフォーマンス測定](#パフォーマンス測定)

## プロジェクト構造

### 推奨ディレクトリ構成

```
src/hibikasu_agent/
├── __init__.py              # パッケージエクスポート
├── py.typed                 # 型情報マーカー
├── types.py                 # 型定義
├── core/                    # コアビジネスロジック
│   ├── __init__.py
│   └── example.py
├── utils/                   # ユーティリティ
│   ├── __init__.py
│   ├── profiling.py         # パフォーマンス測定
│   └── helpers.py           # ヘルパー関数
└── cli/                     # CLI関連（必要に応じて）
    ├── __init__.py
    └── commands.py
```

### モジュール分割の原則

1. **core/**: ビジネスロジックの中核
2. **utils/**: 再利用可能なユーティリティ
3. **types.py**: 型定義の集約
4. **cli/**: コマンドラインインターフェース

## コーディングパターン

### 1. 型ヒントの活用

```python
from typing import Protocol
from dataclasses import dataclass

# データクラスの使用
@dataclass
class Config:
    name: str
    max_items: int = 100
    enable_validation: bool = True
    
    def __post_init__(self) -> None:
        if self.max_items <= 0:
            raise ValueError("max_items must be positive")

# Protocolの活用
class DataProcessor(Protocol):
    def process(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process data and return result."""
        ...
```

### 2. エラーハンドリングのパターン

```python
# 具体的で実用的なエラーメッセージ
def validate_config(config: dict[str, Any]) -> None:
    if "name" not in config:
        raise ValueError(
            "Missing required field 'name' in configuration. "
            "Please provide a valid name string."
        )
    
    if not isinstance(config["name"], str):
        raise TypeError(
            f"Expected 'name' to be str, got {type(config['name']).__name__}. "
            f"Please provide a string value."
        )
```

### 3. ロギングパターン
```python
import logging

logger = logging.getLogger(__name__)

def process_data(items: list[dict]) -> list[dict]:
    logger.info(f"Processing {len(items)} items")
    # 処理ロジック
    logger.info("Processing completed")
```

## テストパターン

### 1. 単体テスト

```python
import pytest
from hibikasu_agent.core.example import ExampleConfig

class TestExampleConfig:
    def test_正常系_有効な設定で作成できる(self) -> None:
        """有効な設定でインスタンスが作成できることを確認。"""
        config = ExampleConfig(name="test", max_items=10)
        
        assert config.name == "test"
        assert config.max_items == 10
        assert config.enable_validation is True
    
    def test_異常系_不正な値でエラー(self) -> None:
        """不正な値でValueErrorが発生することを確認。"""
        with pytest.raises(ValueError, match="max_items must be positive"):
            ExampleConfig(name="test", max_items=0)
```

### 3. 統合テスト

```python
def test_統合_設定とプロセッサの連携(tmp_path):
    """設定とデータ処理の統合動作を確認。"""
    # 設定ファイル作成
    config_file = tmp_path / "config.json"
    config_file.write_text('{"name": "test", "max_items": 5}')
    
    # 設定読み込み
    config = load_config(config_file)
    processor = DataProcessor(config)
    
    # データ処理
    result = processor.process([{"id": 1, "value": 10}])
    
    assert len(result) == 1
    assert result[0]["processed"] is True
```

## パフォーマンス測定
### プロファイリングの活用

```python
from hibikasu_agent.utils.profiling import profile, Timer

# 関数デコレーター
@profile
def heavy_computation(data: list[int]) -> int:
    return sum(x**2 for x in data)

# コンテキストマネージャー
def process_large_dataset(data: list[dict]) -> list[dict]:
    with Timer("Large dataset processing") as timer:
        result = []
        for item in data:
            processed = complex_transform(item)
            result.append(processed)
    
    logger.info(f"Processing took {timer.elapsed:.2f} seconds")
    return result
```

### ベンチマークテスト

## ファイル操作パターン

### 設定ファイルの処理

```python
from pathlib import Path
import json
from typing import Any

def load_config(config_path: Path) -> dict[str, Any]:
    """設定ファイルを安全に読み込む。"""
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}. "
            f"Create one with: touch {config_path}"
        )
    
    try:
        with config_path.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON in {config_path}: {e}. "
            f"Please check the file format."
        ) from e
```

## CLI パターン

### Click を使用したCLI

```python
import click
from hibikasu_agent.core.example import ExampleConfig

@click.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def main(config: str, verbose: bool) -> None:
    """A short description of the project"""
    if verbose:
        setup_logging(level="DEBUG")
    
    if config:
        cfg = load_config(Path(config))
    else:
        cfg = ExampleConfig(name="default")
    
    # メインロジック実行
    result = process_data(cfg)
    click.echo(f"Processed {len(result)} items")
```

## まとめ

これらのパターンを参考に、一貫性のある保守性の高いコードを書いてください。

- **型ヒント**: 必ず使用
- **エラーメッセージ**: 具体的で実用的に
- **ロギング**: 適切なレベルで構造化
- **テスト**: 単体・統合・プロパティベースを組み合わせ
- **ドキュメント**: コードの意図を明確に

詳細な実装例は `src/` および `tests/` ディレクトリを参照してください。