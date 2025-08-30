#!/usr/bin/env python
"""Main agent script for ADK Web integration."""

from hibikasu_agent.agents.facilitator_agent import FacilitatorAgent
from hibikasu_agent.schemas import Persona, ProjectSettings


def create_sample_personas() -> list[Persona]:
    """Create sample personas for testing."""
    return [
        Persona(
            name="佐藤 拓也",
            age=28,
            occupation="IT企業のソフトウェアエンジニア",
            personality="新しい技術やガジェットに興味があり、効率性を重視する。健康にも関心があるが、仕事が忙しくて運動不足気味。",
        ),
        Persona(
            name="田中 美咲",
            age=35,
            occupation="マーケティング会社のプランナー",
            personality="トレンドに敏感で、SNSでの情報発信も積極的。美容と健康に関心が高く、オーガニック製品を好む。",
        ),
        Persona(
            name="山田 健太",
            age=42,
            occupation="中小企業の営業部長",
            personality="コストパフォーマンスを重視する現実主義者。家族との時間を大切にし、子供の教育にも熱心。",
        ),
    ]


# Create project settings
project_settings = ProjectSettings(
    project_name="フォーカスグループ議論テスト",
    topic="新しいエナジードリンクのコンセプトについてどう思いますか？健康志向でオーガニック素材を使用し、カフェインは控えめです。",
    personas=create_sample_personas(),
    project_overview="AI仮想フォーカスグループによる商品コンセプト評価",
)

# Create facilitator agent
facilitator_agent = FacilitatorAgent(
    project_settings=project_settings,
    model="gemini-2.5-flash",
    max_turns=5,
)

# Export the main agent for ADK Web
root_agent = facilitator_agent.agent
