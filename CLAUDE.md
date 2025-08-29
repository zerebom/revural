# Hibikasu Agent - プロジェクト仕様書

## プロジェクト概要

Hibikasu Agentは、Google ADK (Agent Development Kit) を活用した仮想フォーカスグループシステムです。複数のAIペルソナが自然な議論を展開し、プロダクトマネージャーやマーケティング担当者が新商品・サービスに対する多様な意見を効率的に収集できる環境を提供します。

### 主要機能
- **マルチエージェント議論システム**: 異なるペルソナを持つ複数のAIエージェントが自律的に議論
- **カスタマイズ可能なペルソナ設定**: 年齢、職業、性格、価値観などを詳細に設定可能
- **議論ログの永続化**: JSON形式での議論履歴保存と再生機能
- **インサイト抽出**: 議論から重要な洞察を自動抽出（開発中）

### 技術スタック
- **言語**: Python 3.12+
- **フレームワーク**: Google ADK (Agent Development Kit)
- **LLMモデル**: Gemini (gemini-2.5-flash-lite)
- **パッケージ管理**: uv
- **データ形式**: JSON, Pydantic models

## エージェント構成

### 実装済みエージェント
1. **Persona Agent** (`src/hibikasu_agent/agents/persona_agent.py`)
   - 設定されたペルソナに基づいて議論に参加
   - 個性的な発言パターンと価値観を表現
   - プロンプトベースの柔軟な性格設定

### 開発予定エージェント
2. **Facilitator Agent**: 議論の進行管理と話題転換
3. **Analyst Agent**: 議論内容の分析とインサイト生成
4. **Archivist Agent**: データベース連携と長期記憶管理

## 詳細ガイドの参照

### コードベース構造
- `src/hibikasu_agent/agents/`: エージェント実装とプロンプト定義
- `src/hibikasu_agent/schemas/`: Pydanticモデルによるデータスキーマ定義
- `src/hibikasu_agent/utils/`: ロギング設定とヘルパー関数
- `tests/scripts/`: 実行可能なテストスクリプト（議論シミュレーション）

### 重要ファイル
- `tests/scripts/run_discussion.py`: 議論シミュレーションの実行スクリプト
- `src/hibikasu_agent/agents/prompts.py`: エージェントプロンプトのテンプレート
- `src/hibikasu_agent/schemas/models.py`: 議論データモデルの定義

### 開発パターン
- `docs/development-patterns.md`: 推奨される開発パターンとベストプラクティス
- 型ヒントとPydanticモデルを活用した厳密な型管理
- 構造化ロギングによるデバッグ支援
- テスト駆動開発とプロパティベーステスト

## 開発時の注意事項

### Google ADK関連
- APIキーの環境変数設定が必須（`GOOGLE_API_KEY`）
- レート制限に注意（特にgemini-2.5-flash-liteモデル使用時）
- プロンプトエンジニアリングでペルソナの個性を表現

### エージェント間通信
- 現在は同期的な順次発言方式
- 将来的には非同期メッセージパッシングの実装を検討
- 議論の自然性を保つためのターン制御ロジック

### データ永続化
- 議論ログはJSON形式で保存
- タイムスタンプと発言者情報を含む詳細なログ
- 将来的にはSQLiteやPostgreSQLへの移行を検討

## テストとデバッグ

### 議論シミュレーション実行
```bash
# 基本実行
python tests/scripts/run_discussion.py

# デバッグモード
python tests/scripts/run_discussion.py --debug

# カスタムトピック
python tests/scripts/run_discussion.py --topic "新商品のアイデア"
```

### 開発コマンド
```bash
make test      # テスト実行
make lint      # リンターチェック
make format    # コードフォーマット
make typecheck # 型チェック
```