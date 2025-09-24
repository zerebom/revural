# 4人→9人エージェント拡張 実装変更ポイント

## 概要

Hibikasu Agentのエージェント数を4人から9人に拡張する際の詳細な変更ポイントを整理します。

## 変更が必要なファイル・箇所

### 1. バックエンド（Python）

#### 1.1 エージェント定義
**ファイル**: `src/hibikasu_agent/constants/agents.py`

**変更内容**:
- 新しい5つのエージェントキー定数を追加
  ```python
  DATA_SCIENTIST_AGENT_KEY: Final[str] = "data_scientist_specialist"
  UX_WRITER_AGENT_KEY: Final[str] = "ux_writer_specialist"
  SECURITY_SPECIALIST_AGENT_KEY: Final[str] = "security_specialist_specialist"
  MARKETING_STRATEGIST_AGENT_KEY: Final[str] = "marketing_strategist_specialist"
  LEGAL_ADVISOR_AGENT_KEY: Final[str] = "legal_advisor_specialist"
  ```

- 新しい5つのstate_key定数を追加
  ```python
  DATA_SCIENTIST_ISSUES_STATE_KEY: Final[str] = "data_scientist_issues"
  UX_WRITER_ISSUES_STATE_KEY: Final[str] = "ux_writer_issues"
  SECURITY_SPECIALIST_ISSUES_STATE_KEY: Final[str] = "security_specialist_issues"
  MARKETING_STRATEGIST_ISSUES_STATE_KEY: Final[str] = "marketing_strategist_issues"
  LEGAL_ADVISOR_ISSUES_STATE_KEY: Final[str] = "legal_advisor_issues"
  ```

- `SPECIALIST_DEFINITIONS`タプルに新しい5つのSpecialistDefinitionを追加

#### 1.2 プロンプト定義
**ファイル**: `prompts/agents.toml`

**変更内容**:
- 新しい5つのエージェントセクションを追加
  - `[data_scientist]`
  - `[ux_writer]`
  - `[security_specialist]`
  - `[marketing_strategist]`
  - `[legal_advisor]`

/docs/250922/new_agents_prompts.mdを参照してください

各セクションに以下を定義:
- `instruction_review`: レビュー時の専門的観点とプロンプト
- `instruction_chat`: チャット時の応答スタイル
- チャットは一回の応答が200文字くらいになるようにしてください

#### 1.3 エージェント実装
**重要**: 個別のエージェントディレクトリ作成は**不要**です。

**理由**:
- 各エージェントの`agent.py`は`create_specialist_for_role(role)`を呼ぶだけ（6行のみ）
- 実際のロジックは`specialist.py`の共通ファクトリで処理
- エージェント固有設定は以下2ファイルで管理:
  1. `constants/agents.py`のSpecialistDefinition
  2. `prompts/agents.toml`のプロンプト定義


### 2. フロントエンド（TypeScript/React）

#### 2.1 プリセット定義
**ファイル**: `frontend/lib/presets.ts`

**変更内容**:
- 各プリセットの`roles`配列を**MAX4人以内**で再構成
- 既存プリセットの調整と新しいプリセットの追加検討

**制約**: プリセットは最大4人までのエージェント組み合わせとする

例:
```typescript
export const TEAM_PRESETS: TeamPreset[] = [
  {
    id: "technical-core",
    name: "技術コアチーム",
    description: "技術・セキュリティ・品質の観点でレビュー",
    roles: ["engineer", "security_specialist", "qa_tester", "data_scientist"],
  },
  {
    id: "product-ux",
    name: "プロダクト・UXチーム",
    description: "プロダクト・UX・ライティングの観点でレビュー",
    roles: ["pm", "ux_designer", "ux_writer", "marketing_strategist"],
  },
  {
    id: "compliance-quality",
    name: "コンプライアンス・品質チーム",
    description: "法務・セキュリティ・品質・データの観点でレビュー",
    roles: ["legal_advisor", "security_specialist", "qa_tester", "data_scientist"],
  },
  {
    id: "business-strategy",
    name: "ビジネス戦略チーム",
    description: "ビジネス・マーケティング・UXの観点でレビュー",
    roles: ["pm", "marketing_strategist", "ux_designer", "data_scientist"],
  },
]
```

**注意**: 9人全員を一度に選択したい場合は、プリセットではなく個別選択機能を使用する

#### 2.2 ユーティリティ関数
**ファイル**: `frontend/lib/utils.ts`

**変更内容**:
- `getAgentColor`関数に新しいエージェントの色分け追加
- その他のエージェント判定ロジックの更新

#### 2.3 型定義
**ファイル**: `frontend/lib/types.ts`

**確認・更新内容**:
- `SpecialistDefinition`型が新しいフィールドに対応しているか確認
- 必要に応じて型定義を更新

### 4. テストファイル

#### 4.1 単体テスト
**更新が必要なファイル**:
- `tests/unit/test_agent_selection.py`
  - `test_get_specialist_agent_keys`の期待値を9個に更新
  - 新しいエージェントキーのテスト追加

- `tests/unit/test_tools.py`
  - `SPECIALIST_DEFINITIONS`の参照箇所の更新

- `tests/unit/services/test_api_issue_mapper.py`
  - 新しいエージェントのテストケース追加

#### 4.2 API統合テスト
**更新が必要なファイル**:
- `tests/api/test_review_with_selected_agents.py`
  - 新しいエージェントを含むテストケース追加

- `tests/api/test_agents_roles_endpoint.py`
  - `/agents/roles`エンドポイントが9個のロールを返すことを検証

### 5. サービス層

#### 5.1 ADKプロバイダー
**ファイル**: `src/hibikasu_agent/services/providers/adk.py`

**変更内容**:
- `DEFAULT_SELECTED_AGENTS`リストの更新（必要に応じて）
- `get_available_agents`メソッドの動作確認

## 実装順序

### Phase 1: バックエンド基盤構築
**目標**: 新5エージェントのコア定義を追加
**工数**: 2-3時間

#### Phase 1 Todolist
- [ ] `src/hibikasu_agent/constants/agents.py`に新5エージェントのキー定数追加
  - `DATA_SCIENTIST_AGENT_KEY`, `UX_WRITER_AGENT_KEY`, `SECURITY_SPECIALIST_AGENT_KEY`, `MARKETING_STRATEGIST_AGENT_KEY`, `LEGAL_ADVISOR_AGENT_KEY`
  - 対応するSTATE_KEY定数追加
- [ ] `src/hibikasu_agent/constants/agents.py`のSPECIALIST_DEFINITIONSタプルに新5エージェント追加
  - data_scientist (高橋 健太)
  - ux_writer (田中 結衣)
  - security_specialist (イヴァン・ペトロフ)
  - marketing_strategist (クロエ・デュポン)
  - legal_advisor (サミュエル・ジョーンズ)
- [ ] `prompts/agents.toml`に新5エージェントのプロンプト定義追加
  - `/docs/250922/new_agents_prompts.md`の内容を参考に実装
  - instruction_review, instruction_chat の両方を定義
- [ ] 基本動作テスト: `create_specialist_for_role("data_scientist")`が正常動作することを確認

### Phase 2: フロントエンド対応
**目標**: UI側で9人エージェントが選択・表示可能にする
**工数**: 1-2時間

#### Phase 2 Todolist
- [ ] `frontend/lib/presets.ts`の更新（MAX4人制約を維持）
  - 既存プリセットが4人以内であることを確認
  - 新しい4人構成のプリセット追加（技術特化、ビジネス特化など）
- [ ] `frontend/lib/utils.ts`の`getAgentColor`関数更新
  - 新5エージェント用の色分け追加
  - エージェント名判定ロジックの更新
- [ ] `frontend/public/avatars/`に新5エージェントのアバター画像追加
  - `data_scientist.png`, `ux_writer.png`, `security_specialist.png`, `marketing_strategist.png`, `legal_advisor.png`
  - アバター未追加時の暫定対応（文字ベースアバター）
- [ ] フロントエンド表示テスト: 9人全員がMemberSelectGridで正常表示されることを確認

### Phase 3: テスト更新・修正
**目標**: 既存テストを9人体制に対応させる
**工数**: 1-2時間

#### Phase 3 Todolist
- [ ] `tests/unit/test_agent_selection.py`の更新
  - `test_get_specialist_agent_keys`の期待値を4→9に変更
  - 新エージェントキーのテスト追加
- [ ] `tests/unit/test_tools.py`の更新
  - `SPECIALIST_DEFINITIONS`参照箇所の確認・修正
- [ ] `tests/unit/services/test_api_issue_mapper.py`の更新
  - 新5エージェント用のテストケース追加
- [ ] `tests/api/test_review_with_selected_agents.py`の更新
  - 新エージェントを含むテストケース追加
- [ ] `tests/api/test_agents_roles_endpoint.py`の更新
  - `/agents/roles`エンドポイントが9個のロールを返すことを検証
- [ ] 全テスト実行: `make test`でPASSすることを確認

### Phase 4: 統合検証・最終確認
**目標**: システム全体の動作確認と品質保証
**工数**: 1-2時間

#### Phase 4 Todolist
- [ ] API動作確認
  - `/agents/roles`エンドポイントが9個のロールを正常返却
  - 各新エージェントでのレビュー実行テスト
  - エラーハンドリングの確認
- [ ] フロントエンド統合テスト
  - 9人全員の選択・解除動作確認
  - プリセット選択動作確認（MAX4人制約）
  - 新エージェントのアバター表示確認
- [ ] パフォーマンステスト
  - 9人同時レビュー実行時の応答時間確認
  - 必要に応じてタイムアウト設定調整
- [ ] 最終検証
  - 既存4人エージェントの動作に影響がないことを確認
  - ドキュメント更新（必要に応じて）
  - リリースノート作成準備

### 【オプション】Phase 5: 共通プロンプト構造化
**目標**: 将来の保守性向上のための構造改善
**工数**: 5-8時間

#### Phase 5 Todolist（発展的改善）
- [ ] `specialist.py`に`build_instruction_from_template`関数実装
- [ ] `agents.toml`を共通パーツ構造に移行
  - [common]セクション追加
  - 各エージェントを固有パーツに分離
- [ ] 後方互換性確保テスト
- [ ] 段階的移行（1エージェントずつ新形式に移行）
- [ ] 全エージェントの新形式移行完了

## 注意事項


### プリセット制約
- **重要**: プリセットに含められるエージェント数は最大4人まで
- 理由: パフォーマンスとユーザビリティのバランスを考慮

### パフォーマンス
- 必要に応じてタイムアウト設定の調整
- プリセット制限により通常は最大4人並列実行

### データ整合性
- エージェントキーの命名規則を統一
- state_keyとagent_keyの対応関係を維持

## 確認ポイント

### 実装完了後のチェックリスト
- [ ] `/agents/roles` APIが9個のロールを返す
- [ ] 各エージェントでレビューが正常実行される
- [ ] フロントエンドで9人全員が選択可能
- [ ] プリセットが正常に動作する
- [ ] アバター画像が正しく表示される
- [ ] 全テストがPASSする

## 発展的改善案：共通プロンプト構造化

### 概要
`agents.toml`に共通パーツを定義し、Pythonアプリケーション側で動的に結合する実装。保守性と拡張性を大幅に向上させます。

### メリット
- **保守性向上**: 共通の出力仕様を1箇所で管理
- **重複コード削減**: エージェント固有部分と共通部分の明確な分離
- **スケーラビリティ**: 新エージェント追加が容易

### 実装工数
**総工数: 5-8時間程度**
1. `specialist.py`の拡張（2-3時間）
2. `agents.toml`構造変更（1-2時間）
3. テスト・検証（2-3時間）

### 詳細設計
詳細は `/docs/250922/common_prompt_structure.md` を参照

### 推奨
長期的な保守性を考慮すると、この共通化アプローチでの実装を強く推奨します。
