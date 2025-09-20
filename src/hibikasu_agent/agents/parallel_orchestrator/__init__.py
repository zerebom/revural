"""Parallel orchestrator exports."""

from pathlib import Path

from google.adk.agents import config_agent_utils

from .agent import create_coordinator_agent


def load_review_pipeline() -> object:
    """Load the YAML-defined review pipeline agent."""

    config_path = Path(__file__).with_name("root_agent.yaml")
    return config_agent_utils.from_config(config_path)


__all__ = ["create_coordinator_agent", "load_review_pipeline"]
