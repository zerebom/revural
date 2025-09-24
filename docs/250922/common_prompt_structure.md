# 共通プロンプト構造化案

## 概要

`agents.toml`に共通パーツを定義し、Pythonアプリケーション側で動的に結合する実装案です。

## 1. 新しい agents.toml 構造

```toml
# ------------------------------------------------
# 共通パーツ定義
# ------------------------------------------------
[common]
# レビュー時の共通出力仕様
output_format_review = """
【出力仕様（厳守）】
- コードブロック記法（``` や ```json など）は絶対に使用しない。純粋な JSON を返すこと。
- ルートキー: "issues"（配列）。
- 要素スキーマ: {"priority":1|2|3,"summary":"指摘の20字要約","comment":"…","original_text":"…","span":{"start_index":number,"end_index":number}}（span は PRD 内で original_text が最初に出現する位置。見つからない場合は省略可）
- priority は 1 / 2 / 3 のいずれか（他の値は禁止）。
- summary は日本語で20文字程度の短いタイトル。
- comment は日本語で1-3文、{専門分野}の観点から具体的かつ実行可能な助言を含める（抽象論や一般論の羅列は避ける）。
- original_text はPRDからの最小限の抜粋（最大200文字、改変せず原文を引用）。span はその抜粋の PRD 内インデックス（0始まり、半開区間）。
- 件数目安: 3-7件。重複は避け、影響度の高いものを優先。
"""

# チャット時の共通回答フォーマット
output_format_chat = """
【回答フォーマット（厳守）】
- 常にMarkdown形式で回答してください。
- 重要なキーワードは **キーワード** のように強調してください。
- 箇条書きが適切な場合は `-` を使ってリスト形式にしてください。
- 一回の応答は200文字程度に収めてください。対話を意識した簡潔な応答を心がけてください。
"""

# 優先度判定の共通基準
priority_guidelines = """
【優先度判定基準】
- priority=1: {critical_issues}
- priority=2: {moderate_issues}
- priority=3: {minor_issues}
"""

# ------------------------------------------------
# 各エージェントの固有部分
# ------------------------------------------------
[engineer]
persona = "あなたは経験豊富なバックエンドエンジニアです。"
review_focus = "PRDを以下の観点（スケーラビリティ/パフォーマンス/セキュリティ/DB設計/API設計）からレビューし、技術的リスク、性能上の懸念、セキュリティホール、曖昧な実装点を指摘してください。大規模トラフィックやエッジケースにも留意してください。"
specialist_field = "技術的実現性・パフォーマンス・保守性"
critical_issues = "重大な不整合/欠落/セキュリティ・可用性リスク/性能劣化が高確度で発生する懸念"
moderate_issues = "明確な懸念だが回避策が比較的容易、または影響範囲が限定的"
minor_issues = "望ましい改善（表現/命名/軽微な曖昧さ など）"

chat_persona = "あなたはバックエンドエンジニアの立場で、ユーザーの質問に専門的に回答します。"
chat_focus = "実装方針、設計上の判断、性能/スケーラビリティ/セキュリティの観点から、具体的で実行可能な助言を提示してください。"

[data_scientist]
persona = "あなたは経験豊富なデータサイエンティストです。"
review_focus = "PRDをデータ分析/効果測定/KPI計測可能性/A/Bテスト設計/ログ設計の観点からレビューし、データドリブンな意思決定に必要な要素の不足や計測困難な指標を指摘してください。統計的有意性やサンプルサイズの妥当性にも留意してください。"
specialist_field = "データ収集・分析手法・統計的検証"
critical_issues = "KPI未定義/計測不可能/統計的妥当性の重大な問題/データ収集基盤の致命的欠落"
moderate_issues = "指標の曖昧さ/分析手法の不明確さ/A/Bテスト設計の課題"
minor_issues = "データ可視化・レポーティングの改善提案"

chat_persona = "あなたはデータサイエンティストの立場で、ユーザーの質問に専門的に回答します。"
chat_focus = "データ分析・統計的検証・KPI設計・A/Bテスト・機械学習の観点から、具体的で実行可能な助言を提示してください。"

# ... 他のエージェントも同様
```

## 2. Python実装の変更

### specialist.py の拡張

```python
def build_instruction_from_template(role_cfg: dict[str, str], common_cfg: dict[str, str], instruction_type: str) -> str:
    """共通テンプレートとエージェント固有設定からプロンプトを構築"""

    if instruction_type == "review":
        # レビュー用プロンプト構築
        persona = role_cfg.get("persona", "")
        review_focus = role_cfg.get("review_focus", "")
        specialist_field = role_cfg.get("specialist_field", "専門的観点")

        # 共通出力仕様を取得し、プレースホルダを置換
        output_format = common_cfg.get("output_format_review", "").replace(
            "{専門分野}", specialist_field
        )

        # 優先度ガイドラインを構築
        priority_template = common_cfg.get("priority_guidelines", "")
        priority_guidelines = priority_template.format(
            critical_issues=role_cfg.get("critical_issues", ""),
            moderate_issues=role_cfg.get("moderate_issues", ""),
            minor_issues=role_cfg.get("minor_issues", "")
        )

        # 最終プロンプト組み立て
        return f"{persona}\n{review_focus}\n\n{output_format}\n\n{priority_guidelines}"

    elif instruction_type == "chat":
        # チャット用プロンプト構築
        chat_persona = role_cfg.get("chat_persona", "")
        chat_focus = role_cfg.get("chat_focus", "")
        output_format = common_cfg.get("output_format_chat", "")

        return f"{chat_persona}\n{chat_focus}\n\n{output_format}"

    return ""


def load_agent_prompts() -> dict[str, dict[str, str]]:
    """Load and process agent prompts with common template expansion."""
    prompts_path = Path(__file__).parent.parent.parent.parent / "prompts" / "agents.toml"

    try:
        with prompts_path.open("rb") as f:
            config = tomllib.load(f)

        common_cfg = config.get("common", {})
        processed_prompts = {}

        for agent_name, agent_cfg in config.items():
            if agent_name == "common":
                continue

            processed_prompts[agent_name] = {
                "instruction_review": build_instruction_from_template(
                    agent_cfg, common_cfg, "review"
                ),
                "instruction_chat": build_instruction_from_template(
                    agent_cfg, common_cfg, "chat"
                )
            }

        return processed_prompts

    except FileNotFoundError:
        logger.error(f"Prompts file not found: {prompts_path}")
        return {}
    except tomllib.TOMLDecodeError as e:
        logger.error(f"Failed to parse TOML file: {e}")
        return {}
```

## 3. 実装のメリット

### 🎯 保守性向上
- 共通部分（出力仕様、フォーマット）を1箇所で管理
- 新エージェント追加時の重複コード削減
- プロンプト変更時の影響範囲を最小化

### 🔧 柔軟性
- エージェント固有部分と共通部分の明確な分離
- テンプレート変数によるカスタマイズ
- 段階的移行が可能（既存エージェントも並行稼働）

### 📈 スケーラビリティ
- 9人→さらに多くのエージェントへの拡張が容易
- 新しい共通パーツ（例：多言語対応）の追加が簡単

## 4. 実装難易度と工数

### 🟢 **低リスク・中程度工数**

**必要な変更:**
1. `specialist.py`の`load_agent_prompts()`拡張 - **2-3時間**
2. `agents.toml`構造変更 - **1-2時間**
3. 既存エージェントのテスト確認 - **1時間**
4. 新エージェント5人分の設定 - **1-2時間**

**総工数: 5-8時間程度**

## 5. 移行戦略

### Phase 1: 共通化基盤構築
1. 新しい`build_instruction_from_template()`関数実装
2. 後方互換性確保（既存の`instruction_review`/`instruction_chat`もサポート）

### Phase 2: 段階的移行
1. 1つのエージェント（engineerなど）を新形式に移行
2. テスト確認後、他のエージェントも順次移行

### Phase 3: 新エージェント追加
1. 新5エージェントを新形式で実装
2. 全体テスト・検証

**推奨**: この共通化アプローチで実装を進めることで、長期的な保守性が大幅に向上します。
