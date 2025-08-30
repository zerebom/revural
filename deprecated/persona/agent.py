"""Persona Agent for ADK integration."""

from google.adk.agents import LlmAgent
from hibikasu_agent.schemas import Persona


def create_persona_agent(persona: Persona, model: str = "gemini-2.5-flash") -> LlmAgent:
    """Create a Persona Agent compatible with ADK structure.

    Args:
        persona: The persona configuration.
        model: The LLM model to use.

    Returns:
        An ADK LlmAgent configured for this persona.
    """
    instruction = f"""
あなたは以下のペルソナとして議論に参加してください。

【ペルソナ設定】
名前: {persona.name}
年齢: {persona.age}歳
職業: {persona.occupation}
性格・価値観: {persona.personality}

【議論のルール】
1. あなたは「{persona.name}」として、一人称で発言してください。
2. 他の参加者の意見に具体的に言及し、賛成、反対、または深掘りする質問をしてください。
3. 自分の意見だけを言うのではなく、会話のキャッチボールを意識してください。
4. 一度の発言は3〜4文程度の簡潔なものにしてください。
5. 設定された性格や価値観に一貫性を持って発言してください。
"""

    root_agent = LlmAgent(
        name=f"persona_{persona.name.replace(' ', '_')}",
        model=model,
        description=f"AI persona: {persona.name} - {persona.occupation}",
        instruction=instruction.strip(),
    )

    return root_agent
