#!/usr/bin/env python
"""Test script for Specialist Agent PRD review."""

import argparse
import json
import sys
from pathlib import Path

import toml

from hibikasu_agent.agents.specialist import (
    create_engineer_agent,
    create_pm_agent,
    create_qa_tester_agent,
    create_ux_designer_agent,
)
from hibikasu_agent.utils.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


def load_prd_text(prd_path: Path) -> str:
    """Load PRD text from file."""
    if not prd_path.exists():
        raise FileNotFoundError(f"PRD file not found: {prd_path}")

    return prd_path.read_text(encoding="utf-8")


def load_agent_prompts(prompts_path: Path) -> dict:
    """Load agent prompts from TOML file."""
    if not prompts_path.exists():
        raise FileNotFoundError(f"Prompts file not found: {prompts_path}")

    return toml.load(prompts_path)


def create_agent_by_name(agent_name: str, model: str = "gemini-2.5-flash"):
    """Create specialist agent by name."""
    agent_creators = {
        "engineer": create_engineer_agent,
        "ux_designer": create_ux_designer_agent,
        "qa_tester": create_qa_tester_agent,
        "pm": create_pm_agent,
    }

    if agent_name not in agent_creators:
        available = ", ".join(agent_creators.keys())
        raise ValueError(f"Unknown agent: {agent_name}. Available: {available}")

    return agent_creators[agent_name](model)


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Test Specialist Agent PRD review"
    )
    parser.add_argument(
        "--prd",
        type=str,
        required=True,
        help="Path to PRD file (.md)",
    )
    parser.add_argument(
        "--prompts",
        type=str,
        default="prompts/agents.toml",
        help="Path to agent prompts configuration file",
    )
    parser.add_argument(
        "--agent",
        type=str,
        required=True,
        choices=["engineer", "ux_designer", "qa_tester", "pm"],
        help="Specialist agent to test",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path for review results",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash",
        help="LLM model to use",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(level=log_level)

    try:
        # Load PRD text
        prd_path = Path(args.prd)
        prd_text = load_prd_text(prd_path)
        logger.info(f"Loaded PRD from {prd_path} ({len(prd_text)} characters)")

        # Load prompts configuration
        prompts_path = Path(args.prompts)
        load_agent_prompts(prompts_path)
        logger.info(f"Loaded prompts from {prompts_path}")

        # Create specialist agent
        agent = create_agent_by_name(args.agent, args.model)
        logger.info(f"Created specialist agent: {agent}")

        # Generate review
        logger.info("Starting PRD review...")
        review_result = agent.generate_issues_from_prd(prd_text)

        # Parse and validate JSON
        try:
            issues = json.loads(review_result)
            logger.info(f"Review completed with {len(issues)} issues")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON output: {e}")
            print(f"Raw output:\n{review_result}")
            sys.exit(1)

        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(review_result, encoding="utf-8")
            logger.info(f"Review results saved to {output_path}")
        else:
            print("\n" + "=" * 60)
            print(f"Review Results from {agent.specialty}")
            print("=" * 60)
            print(json.dumps(issues, ensure_ascii=False, indent=2))

    except Exception as e:
        logger.error(f"Error during review: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
