"""Specialist Agent implementations using Google ADK."""

import tomllib
from collections.abc import Iterable
from pathlib import Path
from typing import cast

from google.adk.agents import LlmAgent
from pydantic import BaseModel as PydanticBaseModel

from hibikasu_agent.constants.agents import ROLE_TO_DEFINITION, SpecialistDefinition
from hibikasu_agent.schemas.models import IssuesResponse
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


def load_agent_prompts() -> dict[str, dict[str, str]]:
    """Load agent prompts from TOML configuration file.

    Returns:
        Dictionary mapping agent names to their prompts
    """
    prompts_path = Path(__file__).parent.parent.parent.parent / "prompts" / "agents.toml"

    try:
        with prompts_path.open("rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        logger.error(f"Prompts file not found: {prompts_path}")
        return {}
    except tomllib.TOMLDecodeError as e:
        logger.error(f"Failed to parse TOML file: {e}")
        return {}


def create_specialist(  # noqa: PLR0913
    *,
    name: str,
    description: str,
    model: str = "gemini-2.5-flash",
    instruction: str | None = None,
    system_prompt: str | None = None,
    task_prompt: str | None = None,
    output_schema: type[PydanticBaseModel] | None = None,
    output_key: str | None = None,
) -> LlmAgent:
    """Generic factory for creating a specialist ``LlmAgent``.

    Args:
        name: Agent unique name.
        description: Human-readable agent description.
        model: LLM model to use.
        instruction: Full instruction text. If provided, used as-is.
        system_prompt: Optional system prompt. Used if ``instruction`` is not provided.
        task_prompt: Optional task prompt. Used with ``system_prompt``.
        output_schema: Pydantic model type for structured output.

    Returns:
        Configured ``LlmAgent`` instance.
    """
    # Use single instruction string (legacy system/task prompts are ignored)
    final_instruction = (instruction or "").strip()

    if not final_instruction:
        logger.warning(f"Empty instruction for specialist agent; name={name}")

    # Call with explicit arguments to satisfy static typing (no **kwargs dict)
    if output_schema is not None and output_key is not None:
        agent = LlmAgent(
            name=name,
            model=model,
            description=description,
            instruction=final_instruction,
            output_schema=output_schema,
            output_key=output_key,
        )
    elif output_schema is not None:
        agent = LlmAgent(
            name=name,
            model=model,
            description=description,
            instruction=final_instruction,
            output_schema=output_schema,
        )
    elif output_key is not None:
        agent = LlmAgent(
            name=name,
            model=model,
            description=description,
            instruction=final_instruction,
            output_key=output_key,
        )
    else:
        agent = LlmAgent(
            name=name,
            model=model,
            description=description,
            instruction=final_instruction,
        )

    logger.info("Specialist Agent created", name=name, model=model)
    return agent


def create_specialist_from_definition(
    definition: SpecialistDefinition,
    *,
    model: str = "gemini-2.5-flash",
) -> LlmAgent:
    """Create a specialist agent using a shared configuration entry."""

    prompts = load_agent_prompts()
    role_cfg = prompts.get(definition.role, {})
    instruction = (role_cfg.get("instruction_review") or "").strip()

    return create_specialist(
        name=definition.agent_key,
        description=definition.review_description,
        model=model,
        instruction=instruction,
        output_schema=cast(type[PydanticBaseModel], IssuesResponse),
        output_key=definition.state_key,
    )


def create_specialist_for_role(
    role: str,
    *,
    model: str = "gemini-2.5-flash",
) -> LlmAgent:
    """Convenience wrapper that builds a specialist from a role identifier."""

    try:
        definition = ROLE_TO_DEFINITION[role]
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Unknown specialist role: {role}") from exc
    return create_specialist_from_definition(definition, model=model)


def create_specialists_from_config(
    definitions: Iterable[SpecialistDefinition],
    *,
    model: str = "gemini-2.5-flash",
) -> list[LlmAgent]:
    """Build review specialists from shared configuration entries."""

    return [create_specialist_from_definition(definition, model=model) for definition in definitions]


def create_role_agents(
    role_key: str,
    *,
    model: str = "gemini-2.5-flash",
    review_output_key: str,
    name_prefix: str | None = None,
) -> tuple[LlmAgent, LlmAgent]:
    """Create both review and chat agents for a given role.

    Returns:
        (review_agent, chat_agent)
    """
    definition = ROLE_TO_DEFINITION.get(role_key)
    if definition is None:  # pragma: no cover - defensive guard
        raise ValueError(f"Unknown specialist role: {role_key}")

    prompts = load_agent_prompts()
    role_cfg = prompts.get(role_key, {})
    prefix = name_prefix or role_key

    review_instruction = (role_cfg.get("instruction_review") or "").strip()
    review_agent = create_specialist(
        name=f"{prefix}_specialist",
        description=f"{role_key} の専門的観点からPRDをレビュー",
        model=model,
        instruction=review_instruction,
        output_schema=cast(type[PydanticBaseModel], IssuesResponse),
        output_key=review_output_key,
    )

    chat_instruction = (role_cfg.get("instruction_chat") or "").strip()
    chat_agent = create_specialist(
        name=f"{prefix}_chat",
        description=f"{role_key} の専門的観点でユーザーの質問に回答",
        model=model,
        instruction=chat_instruction,
    )
    return review_agent, chat_agent
