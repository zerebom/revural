# Hibikasu Agent - 仮想フォーカスグループ AIエージェントシステム

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-latest-green.svg)](https://github.com/astral-sh/uv)
[![Google ADK](https://img.shields.io/badge/google--adk-1.8+-purple.svg)](https://github.com/google/adk-python)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

複数のAIペルソナが議論を行う仮想フォーカスグループ機能を実現するマルチエージェントシステムです。

## 概要

Hibikasu Agentは、Google ADK (Agent Development Kit) を活用した仮想フォーカスグループシステムです。設定されたペルソナに基づいて複数のAIエージェントが自然な議論を展開し、プロダクトマネージャーやマーケティング担当者が新商品やサービスに対する多様な意見を迅速に収集できるよう支援します。

## 主な機能

- **マルチエージェント議論**: 複数のAIペルソナが自然な議論を展開
- **カスタマイズ可能なペルソナ**: 年齢、職業、性格などを細かく設定可能
- **議論ログの保存**: 議論の全履歴をJSON形式で保存
- **分析レポート生成**: 議論から重要なインサイトを抽出（開発中）

## システム構成

### エージェント構成

1. **Persona Agent**: 設定されたペルソナになりきり議論に参加
2. **Facilitator Agent**: 議論全体を管理・調整（開発中）
3. **Analyst Agent**: 議論ログを分析し、インサイトを生成（開発中）
4. **Archivist Agent**: データの永続化を管理（開発中）

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

### 基本的な議論シミュレーション

```bash
# デフォルトの設定で議論を実行
python tests/scripts/run_discussion.py

# カスタムトピックで実行
python tests/scripts/run_discussion.py \
    --topic "新しいスマートフォンアプリのアイデアについて議論してください" \
    --max-turns 10

# 議論ログを指定したファイルに保存
python tests/scripts/run_discussion.py \
    --output my_discussion.json

# デバッグモードで実行
python tests/scripts/run_discussion.py --debug
```

### コマンドラインオプション

- `--topic`: 議論のトピックを指定
- `--output`: 議論ログの保存先パス
- `--max-turns`: 議論のターン数（デフォルト: 5）
- `--model`: 使用するLLMモデル（デフォルト: gemini-2.5-flash）
- `--debug`: デバッグログを有効化

## 開発

### プロジェクト構造

```
hibikasu-agent/
├── src/
│   └── hibikasu_agent/
│       ├── agents/           # エージェント実装
│       │   ├── persona_agent.py
│       │   └── prompts.py
│       ├── schemas/          # データモデル定義
│       │   └── models.py
│       └── utils/            # ユーティリティ
│           └── logging_config.py
├── tests/
│   └── scripts/
│       └── run_discussion.py # テスト用スクリプト
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

## 今後の開発予定

- [ ] Facilitator Agent: 高度な議論管理機能
- [ ] Analyst Agent: 議論分析とインサイト生成
- [ ] Archivist Agent: データベース連携
- [ ] Web UI: ブラウザベースのインターフェース
- [ ] リアルタイム議論観察機能
- [ ] ユーザー介入機能（議論への質問投入）

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて議論してください。
