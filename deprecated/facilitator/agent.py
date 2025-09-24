"""Facilitator agent for ADK Web integration."""

from hibikasu_agent.agents.facilitator_agent import FacilitatorAgent
from hibikasu_agent.schemas.models import Persona, ProjectSettings

# Create sample personas for the facilitator
sample_personas = [
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

# Create project settings for the discussion
project_settings = ProjectSettings(
    project_name="AIフォーカスグループ・デモ",
    topic="新しいエナジードリンクのコンセプトについて議論してください。健康志向でオーガニック素材を使用し、カフェインは控えめです。",
    personas=sample_personas,
    project_overview="多様な視点を持つ参加者による建設的な商品開発議論",
)

# Create the facilitator agent instance
facilitator_agent = FacilitatorAgent(
    project_settings=project_settings,
    model="gemini-2.5-flash-lite",
    max_turns=3,
)

# Export the root_agent for ADK Web
root_agent = facilitator_agent.agent
