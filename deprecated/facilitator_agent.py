"""Facilitator Agent implementation using Google ADK with multi-agent orchestration."""

from google.adk.agents import LlmAgent
from hibikasu_agent.schemas.models import Persona, ProjectSettings, Utterance
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


def create_persona_llm_agent(persona: Persona, model: str = "gemini-2.5-flash") -> LlmAgent:
    """Create an LlmAgent for a persona that returns control to root agent.

    Args:
        persona: The persona configuration.
        model: The LLM model to use.

    Returns:
        LlmAgent configured for the persona with explicit transfer back.
    """
    # Create safe English agent name based on persona
    safe_name = persona.name.replace(" ", "_").replace("　", "_")
    agent_name = f"persona_{safe_name}"

    # Persona instruction with explicit transfer_to_agent to root
    instruction = (
        f"あなたは{persona.name}、{persona.age}歳の{persona.occupation}です。"
        f"性格: {persona.personality}\n\n"
        f"議論において、あなたの立場から意見を述べてください。"
        f"簡潔で自然な日本語で回答し、あなたの専門性と性格を反映した視点を提供してください。"
        f"\n\n【重要】: 発言の流れは以下の通りです："
        f"\n1. 3-4文程度で自分の意見を述べる"
        f"\n2. 発言を終えた後、必ずtransfer_to_agent("
        f"'focus_group_facilitator')を呼び出して司会者に制御を戻す"
        f"\n\nこの手順を必ず実行してください。司会者が議論を継続するために重要です。"
        f"\n他の参加者を直接呼び出すことはありません。必ず司会者に制御を戻してください。"
    )

    description = f"{persona.name} ({persona.occupation}) - {persona.personality[:50]}..."

    agent = LlmAgent(
        name=agent_name,
        model=model,
        description=description,
        instruction=instruction,
    )

    logger.debug(
        "Persona LlmAgent created with explicit root transfer",
        persona_name=persona.name,
        agent_name=agent_name,
        model=model,
    )

    return agent


class FacilitatorAgent:
    """AI Facilitator Agent that manages multi-persona discussions using ADK."""

    def __init__(
        self,
        project_settings: ProjectSettings,
        model: str = "gemini-2.5-flash",
        max_turns: int = 5,
    ):
        """Initialize the Facilitator Agent.

        Args:
            project_settings: Project configuration including personas and topic.
            model: The LLM model to use for the facilitator and personas.
            max_turns: Maximum number of discussion turns.
        """
        self.project_settings = project_settings
        self.model = model
        self.max_turns = max_turns
        self.discussion_log: list[Utterance] = []

        # Create persona agents as simple LlmAgents
        self.persona_agents: list[LlmAgent] = []
        for persona in project_settings.personas:
            agent = create_persona_llm_agent(persona, model)
            self.persona_agents.append(agent)

        # Create facilitator with personas as sub-agents
        self._create_facilitator_agent()

        logger.info(
            "FacilitatorAgent initialized with simple sub-agent structure",
            project_name=project_settings.project_name,
            num_personas=len(project_settings.personas),
            model=model,
            max_turns=max_turns,
        )

    def _create_facilitator_agent(self) -> None:
        """Create the main facilitator LlmAgent with persona sub-agents."""
        # Create facilitator instruction
        instruction = f"""
あなたはAIフォーカスグループの司会者です。以下の議題について議論を進行してください。

【議題】
{self.project_settings.topic}

【参加者】
{chr(10).join([f"- {persona.name} ({persona.occupation})" for persona in self.project_settings.personas])}

【進行方法】
1. 議題を紹介し、佐藤さんから順番に意見を求めてください
2. 各参加者からの意見を聞いた後、簡潔にコメントしてください
3. 全員の意見を聞いた後、議論を総括してください

【重要】参加者に質問する時は必ずtransfer_to_agent()を使用してください：
- 佐藤さんに質問: transfer_to_agent('persona_佐藤_拓也')
- 田中さんに質問: transfer_to_agent('persona_田中_美咲')
- 山田さんに質問: transfer_to_agent('persona_山田_健太')

参加者は自動的に発言を終了し、あなたに制御が戻ります。順次進行してください。
"""

        self.facilitator = LlmAgent(
            name="focus_group_facilitator",
            model=self.model,
            description=(
                "AI司会者として、フォーカスグループの議論を効果的に進行し、"
                "各参加者から多様で建設的な意見を引き出します。"
            ),
            instruction=instruction,
            sub_agents=self.persona_agents,  # PersonaAgentをsub_agentsとして登録
        )

        logger.debug(
            "Facilitator LlmAgent created with persona sub-agents",
            facilitator_name=self.facilitator.name,
            sub_agents=[agent.name for agent in self.persona_agents],
        )

    @property
    def agent(self) -> LlmAgent:
        """Get the main facilitator agent for ADK Web integration."""
        return self.facilitator

    def get_persona_agents(self) -> list[LlmAgent]:
        """Get the list of persona sub-agents."""
        return self.persona_agents

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"FacilitatorAgent(project='{self.project_settings.project_name}', "
            f"personas={len(self.persona_agents)}, "
            f"model='{self.model}')"
        )
