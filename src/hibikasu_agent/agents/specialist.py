"""Specialist Agent implementations using Google ADK."""

import tomllib
from pathlib import Path

from google.adk.agents import LlmAgent

from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


def load_agent_prompts() -> dict[str, dict[str, str]]:
    """Load agent prompts from TOML configuration file.

    Returns:
        Dictionary mapping agent names to their prompts
    """
    prompts_path = (
        Path(__file__).parent.parent.parent.parent / "prompts" / "agents.toml"
    )

    try:
        with prompts_path.open("rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        logger.error(f"Prompts file not found: {prompts_path}")
        return {}
    except tomllib.TOMLDecodeError as e:
        logger.error(f"Failed to parse TOML file: {e}")
        return {}


def create_engineer_agent(model: str = "gemini-2.5-flash") -> LlmAgent:
    """Create Engineer Specialist Agent.

    Args:
        model: LLM model to use

    Returns:
        LlmAgent configured as engineer specialist
    """
    from pydantic import BaseModel, Field

    # Define output schema for structured response
    class IssueItem(BaseModel):
        severity: str = Field(pattern="^(High|Mid|Low)$")
        comment: str = Field(min_length=1)
        original_text: str = Field(default="")

    class IssuesResponse(BaseModel):
        issues: list[IssueItem] = Field(description="List of issues found in the PRD")

    prompts = load_agent_prompts()
    engineer_config = prompts.get("engineer", {})

    system_prompt = engineer_config.get("system_prompt", "").strip()
    task_prompt = engineer_config.get("task_prompt", "").strip()

    instruction = f"{system_prompt}\n\n{task_prompt}".strip()

    agent = LlmAgent(
        name="engineer_specialist",
        model=model,
        description="バックエンドエンジニアの専門的観点からPRDをレビュー",
        instruction=instruction,
        output_schema=IssuesResponse,  # Structured output
    )

    logger.info("Engineer Specialist Agent created", model=model)
    return agent


def create_ux_designer_agent(model: str = "gemini-2.5-flash") -> LlmAgent:
    """Create UX Designer Specialist Agent.

    Args:
        model: LLM model to use

    Returns:
        LlmAgent configured as UX designer specialist
    """
    from pydantic import BaseModel, Field

    # Define output schema for structured response
    class IssueItem(BaseModel):
        severity: str = Field(pattern="^(High|Mid|Low)$")
        comment: str = Field(min_length=1)
        original_text: str = Field(default="")

    class IssuesResponse(BaseModel):
        issues: list[IssueItem] = Field(description="List of issues found in the PRD")

    prompts = load_agent_prompts()
    ux_designer_config = prompts.get("ux_designer", {})

    system_prompt = ux_designer_config.get("system_prompt", "").strip()
    task_prompt = ux_designer_config.get("task_prompt", "").strip()

    instruction = f"{system_prompt}\n\n{task_prompt}".strip()

    agent = LlmAgent(
        name="ux_designer_specialist",
        model=model,
        description="UXデザイナーの専門的観点からPRDをレビュー",
        instruction=instruction,
        output_schema=IssuesResponse,  # Structured output
    )

    logger.info("UX Designer Specialist Agent created", model=model)
    return agent


def create_qa_tester_agent(model: str = "gemini-2.5-flash") -> LlmAgent:
    """Create QA Tester Specialist Agent.

    Args:
        model: LLM model to use

    Returns:
        LlmAgent configured as QA tester specialist
    """
    from pydantic import BaseModel, Field

    # Define output schema for structured response
    class IssueItem(BaseModel):
        severity: str = Field(pattern="^(High|Mid|Low)$")
        comment: str = Field(min_length=1)
        original_text: str = Field(default="")

    class IssuesResponse(BaseModel):
        issues: list[IssueItem] = Field(description="List of issues found in the PRD")

    prompts = load_agent_prompts()
    qa_tester_config = prompts.get("qa_tester", {})

    system_prompt = qa_tester_config.get("system_prompt", "").strip()
    task_prompt = qa_tester_config.get("task_prompt", "").strip()

    instruction = f"{system_prompt}\n\n{task_prompt}".strip()

    agent = LlmAgent(
        name="qa_tester_specialist",
        model=model,
        description="QAテスターの専門的観点からPRDをレビュー",
        instruction=instruction,
        output_schema=IssuesResponse,  # Structured output
    )

    logger.info("QA Tester Specialist Agent created", model=model)
    return agent


def create_pm_agent(model: str = "gemini-2.5-flash") -> LlmAgent:
    """Create PM Specialist Agent.

    Args:
        model: LLM model to use

    Returns:
        LlmAgent configured as PM specialist
    """
    from pydantic import BaseModel, Field

    # Define output schema for structured response
    class IssueItem(BaseModel):
        severity: str = Field(pattern="^(High|Mid|Low)$")
        comment: str = Field(min_length=1)
        original_text: str = Field(default="")

    class IssuesResponse(BaseModel):
        issues: list[IssueItem] = Field(description="List of issues found in the PRD")

    prompts = load_agent_prompts()
    pm_config = prompts.get("pm", {})

    system_prompt = pm_config.get("system_prompt", "").strip()
    task_prompt = pm_config.get("task_prompt", "").strip()

    instruction = f"{system_prompt}\n\n{task_prompt}".strip()

    agent = LlmAgent(
        name="pm_specialist",
        model=model,
        description="プロダクトマネージャーの専門的観点からPRDをレビュー",
        instruction=instruction,
        output_schema=IssuesResponse,  # Structured output
    )

    logger.info("PM Specialist Agent created", model=model)
    return agent
