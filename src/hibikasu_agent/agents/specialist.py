"""Specialist Agent implementations using Google ADK."""

import tomllib
from pathlib import Path

from google.adk.agents import LlmAgent
from pydantic import BaseModel

from hibikasu_agent.schemas import IssuesResponse
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
    output_schema: type[BaseModel] | None = IssuesResponse,
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


def create_specialist_from_role(  # noqa: PLR0913
    role_key: str,
    *,
    name: str,
    description: str,
    model: str = "gemini-2.5-flash",
    purpose: str = "review",  # "review" or "chat"
    output_schema: type[BaseModel] | None = IssuesResponse,
    output_key: str | None = None,
) -> LlmAgent:
    """Create a specialist using prompts loaded by role key.

    Args:
        role_key: Key in TOML under which prompts are stored (e.g., "engineer").
        name: Agent unique name.
        description: Agent description.
        model: LLM model name.
        output_schema: Structured output schema.
    """
    prompts = load_agent_prompts()
    role_cfg = prompts.get(role_key, {})

    # Purpose-specific single instruction keys (no legacy fallbacks)
    if purpose == "chat":
        instr = (role_cfg.get("instruction_chat") or "").strip()
        # For chat, avoid output_schema/output_key to keep transfer unrestricted
        return create_specialist(
            name=name,
            description=description,
            model=model,
            instruction=instr,
            output_schema=None,
            output_key=None,
        )

    # review (default)
    instr = (role_cfg.get("instruction_review") or "").strip()

    # Ensure review uses IssuesResponse schema by default
    output_schema = output_schema or IssuesResponse

    return create_specialist(
        name=name,
        description=description,
        model=model,
        instruction=instr,
        output_schema=output_schema,
        output_key=output_key,
    )


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
    prefix = name_prefix or role_key
    review_agent = create_specialist_from_role(
        role_key,
        name=f"{prefix}_specialist",
        description=f"{role_key} の専門的観点からPRDをレビュー",
        model=model,
        purpose="review",
        output_schema=IssuesResponse,
        output_key=review_output_key,
    )
    chat_agent = create_specialist_from_role(
        role_key,
        name=f"{prefix}_chat",
        description=f"{role_key} の専門的観点でユーザーの質問に回答",
        model=model,
        purpose="chat",
    )
    return review_agent, chat_agent
