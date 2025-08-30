# Hibikasu PRD Reviewer - AIレビューパネル ハッカソンMVP

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-latest-green.svg)](https://github.com/astral-sh/uv)
[![Google ADK](https://img.shields.io/badge/google--adk-1.8+-purple.svg)](https://github.com/google/adk-python)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

プロダクトマネージャー(PdM)が作成したPRD(製品要求仕様書)を、複数の専門的視点を持つAIエージェントがレビューするツール。

## 概要

Hibikasu PRD Reviewerは、Google ADK (Agent Development Kit) を活用したAIレビューパネルシステムです。バックエンドエンジニア、UXデザイナー、QAテスターなど、複数の専門的視点を持つAIエージェントがPRDをレビューし、仕様の抜け漏れやリスクを開発着手前に効率的に特定することを支援します。

## 主な機能

- **マルチエージェントレビュー**: 複数の専門AIエージェントが並行してPRDをレビュー
- **優先順位付けられた論点**: 重要度に応じて整理された指摘事項の提示
- **フォーカスモード**: 最も重要な論点から一つずつ集中して解消
- **対話による深掘り**: 各論点についてAIエージェントと対話して詳細を理解

## システム構成

### エージェント構成

1. **Review Orchestrator Agent**: レビュープロセス全体を管理する司令塔
2. **Specialist Agent**: 専門分野（バックエンド、UX、QA、PM）を担当するレビューエージェント
3. **Archivist Agent**: レビューデータの永続化を管理する記録係

## セットアップ

### 必要要件

- Python 3.12以上
- Google AI Studio APIキー または Vertex AI の設定

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/zerebom/hibikasu-agent.git
cd hibikasu-agent

# 仮想環境の作成と依存関係のインストール
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

### 環境設定

1. `.env.example` を `.env` にコピー:

```bash
cp .env.example .env
```

2. `.env` ファイルを編集してGoogle AI Studio APIキーを設定:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

## 使用方法

### 基本的なPRDレビュー

```bash
# 専門エージェント単体でのレビューテスト
python tests/scripts/run_specialist_review.py \
    --prd sample.md \
    --prompts prompts/agents.toml \
    --agent engineer

# ADK Webサーバーでのインタラクティブレビュー
adk web src/hibikasu_agent/main.py

# デバッグモードで実行
python tests/scripts/run_specialist_review.py --debug
```

### コマンドラインオプション

- `--prd`: レビュー対象のPRDファイルパス
- `--prompts`: エージェントプロンプト設定ファイル
- `--agent`: 使用する専門エージェント（engineer/ux_designer/qa_tester/pm）
- `--output`: レビュー結果の保存先パス
- `--debug`: デバッグログを有効化

## 開発

### プロジェクト構造

```
hibikasu-agent/
├── src/
│   └── hibikasu_agent/
│       ├── main.py           # ADK Web エントリーポイント
│       ├── agents/           # エージェント実装
│       │   ├── orchestrator.py  # Review Orchestrator Agent
│       │   └── specialist.py    # Specialist Agent
│       └── schemas/          # データモデル定義
│           └── models.py
├── prompts/
│   └── agents.toml          # エージェントプロンプト設定
├── tests/
│   └── scripts/
│       └── run_specialist_review.py # テスト用スクリプト
├── pyproject.toml
└── README.md
```

### テストの実行

```bash
# 全テストを実行
make test

# コード品質チェック
make lint
make typecheck

# フォーマット
make format
```

## 開発ロードマップ

### フェーズ1: PoC開発
- [x] Specialist Agent の単体性能テスト
- [ ] プロンプト設計・改良のイテレーション
- [ ] 指摘生成品質の定性評価

### フェーズ2: 統合テスト  
- [ ] Review Orchestrator Agent の実装
- [ ] ADK Web による統合テスト
- [ ] 論点の統合・優先順位付けロジック

### フェーズ3: MVP完成
- [ ] フロントエンド UI 実装
- [ ] フォーカスモード体験の実現
- [ ] 対話による深掘り機能

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて議論してください。
