"""Facilitator Agent implementation using Google ADK with multi-agent orchestration."""

from typing import cast

from google.adk.agents import BaseAgent, LlmAgent

from hibikasu_agent.agents.prompts import create_facilitator_prompt
from hibikasu_agent.schemas import Persona, ProjectSettings, Utterance
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


def create_persona_llm_agent(
    persona: Persona, model: str = "gemini-2.5-flash"
) -> LlmAgent:
    """Create an LlmAgent for a persona that can be used as a sub-agent.

    Args:
        persona: The persona configuration.
        model: The LLM model to use.

    Returns:
        LlmAgent configured for the persona.
    """
    # Create safe English agent name based on persona
    safe_name = persona.name.replace(" ", "_").replace("　", "_")
    agent_name = f"persona_{safe_name}"

    # Create instruction with persona context
    instruction = (
        f"あなたは{persona.name}、{persona.age}歳の{persona.occupation}です。"
        f"性格: {persona.personality}\n\n"
        f"議論において、あなたの立場から意見を述べてください。"
        f"簡潔で自然な日本語で回答し、あなたの専門性と性格を反映した視点を提供してください。"
        f"\n\n【重要】: あなたは議論の参加者として発言するのみです。"
        f"司会者や他の参加者を呼び出すことはありません。"
        f"transfer_to_agent等の関数は使用しないでください。"
    )

    description = (
        f"{persona.name} ({persona.occupation}) - {persona.personality[:50]}..."
    )

    agent = LlmAgent(
        name=agent_name,
        model=model,
        description=description,
        instruction=instruction,
    )

    logger.debug(
        "Persona LlmAgent created",
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

        # Create LlmAgent for each persona as sub-agents
        self.persona_agents: list[LlmAgent] = []
        for persona in project_settings.personas:
            agent = create_persona_llm_agent(persona, model)
            self.persona_agents.append(agent)

        # Create the main facilitator agent with sub-agents
        self._create_facilitator_agent()

        logger.info(
            "FacilitatorAgent initialized",
            project_name=project_settings.project_name,
            num_personas=len(project_settings.personas),
            model=model,
            max_turns=max_turns,
        )

    def _create_facilitator_agent(self) -> None:
        """Create the main facilitator LlmAgent with persona sub-agents."""
        persona_names = [agent.name for agent in self.persona_agents]
        persona_descriptions = [
            f"- {agent.name}: {agent.description}" for agent in self.persona_agents
        ]

        instruction = create_facilitator_prompt(
            topic=self.project_settings.topic,
            persona_descriptions=persona_descriptions,
            max_turns=self.max_turns,
        )

        self.facilitator = LlmAgent(
            name="focus_group_facilitator",
            model=self.model,
            description=(
                "AI司会者として、フォーカスグループの議論を効果的に進行し、"
                "各参加者から多様で建設的な意見を引き出します。"
            ),
            instruction=instruction,
            sub_agents=cast("list[BaseAgent]", self.persona_agents),
        )

        logger.debug(
            "Facilitator LlmAgent created",
            facilitator_name=self.facilitator.name,
            sub_agents=persona_names,
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
