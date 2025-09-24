"""Test persona agent implementation."""

from google.adk.agents import LlmAgent
from hibikasu_agent.schemas.models import Persona

# Create a test persona
test_persona = Persona(
    name="佐藤 拓也",
    age=28,
    occupation="IT企業のソフトウェアエンジニア",
    personality="新しい技術やガジェットに興味があり、効率性を重視する。健康にも関心があるが、仕事が忙しくて運動不足気味。",
)

# Create root_agent as required by ADK
root_agent = LlmAgent(
    name=f"persona_{test_persona.name.replace(' ', '_')}",
    model="gemini-2.5-flash-lite",
    description=f"AI persona: {test_persona.name} - {test_persona.occupation}",
    instruction=(
        f"あなたは{test_persona.name}、{test_persona.age}歳の{test_persona.occupation}です。"
        f"性格: {test_persona.personality}"
        f"日本語で自然に会話してください。"
    ),
)
