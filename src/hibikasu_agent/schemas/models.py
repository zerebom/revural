"""Data models for the Hibikasu virtual focus group agent system."""

from pydantic import BaseModel, Field


class Persona(BaseModel):
    """AIペルソナの属性を定義するモデル."""

    name: str = Field(description="ペルソナの名前 (例: 佐藤 拓也)")
    age: int = Field(description="年齢")
    occupation: str = Field(description="職業 (例: IT企業勤務のソフトウェアエンジニア)")
    personality: str = Field(
        description="性格、価値観、趣味、製品に対するスタンスなどの自由記述"
    )


class ProjectSettings(BaseModel):
    """調査プロジェクト全体の設定を定義するモデル."""

    project_id: str | None = Field(
        default=None, description="システムが付与する一意のプロジェクトID"
    )
    project_name: str = Field(
        description="調査プロジェクト名 (例: 新エナジードリンクのコンセプト評価)"
    )
    topic: str = Field(description="ペルソナたちに議論してほしい議題や質問")
    personas: list[Persona] = Field(description="この調査に参加するペルソナのリスト")
    project_overview: str | None = Field(
        default=None, description="プロジェクトの目的や概要"
    )


class Utterance(BaseModel):
    """議論の中の一つの発言を表すモデル."""

    persona_name: str = Field(description="発言したペルソナの名前")
    content: str = Field(description="発言内容")
    timestamp: str | None = Field(default=None, description="発言のタイムスタンプ")


class DiscussionLog(BaseModel):
    """一連の議論の完全なログを格納するモデル."""

    log: list[Utterance] = Field(description="時系列に並んだ発言のリスト")
    project_id: str | None = Field(default=None, description="関連するプロジェクトID")


class TopicSentiment(BaseModel):
    """キートピックとその感情分析結果を格納するモデル."""

    topic: str = Field(description="議論から抽出されたキートピック")
    positive_count: int = Field(description="そのトピックに対するポジティブな言及の数")
    negative_count: int = Field(description="そのトピックに対するネガティブな言及の数")
    neutral_count: int = Field(description="そのトピックに対する中立的な言及の数")


class AnalysisReport(BaseModel):
    """Analyst Agentが生成する最終的な分析レポートの構造を定義するモデル."""

    summary: str = Field(description="議論全体の要約")
    key_topics: list[TopicSentiment] = Field(
        description="キートピックとそれぞれの感情分析の結果リスト"
    )
    actionable_insights: list[str] = Field(
        description="プロダクトマネージャーが次に取るべき具体的なアクション提案のリスト"
    )
    project_id: str | None = Field(default=None, description="関連するプロジェクトID")
