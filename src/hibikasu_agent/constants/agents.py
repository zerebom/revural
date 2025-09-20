"""Agent-related constant definitions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class SpecialistDefinition:
    """Static configuration describing a specialist agent."""

    role: str
    agent_key: str
    state_key: str
    display_name: str
    review_description: str


ENGINEER_AGENT_KEY: Final[str] = "engineer_specialist"
UX_AGENT_KEY: Final[str] = "ux_designer_specialist"
QA_AGENT_KEY: Final[str] = "qa_tester_specialist"
PM_AGENT_KEY: Final[str] = "pm_specialist"

ENGINEER_ISSUES_STATE_KEY: Final[str] = "engineer_issues"
UX_ISSUES_STATE_KEY: Final[str] = "ux_designer_issues"
QA_ISSUES_STATE_KEY: Final[str] = "qa_tester_issues"
PM_ISSUES_STATE_KEY: Final[str] = "pm_issues"

SPECIALIST_DEFINITIONS: tuple[SpecialistDefinition, ...] = (
    SpecialistDefinition(
        role="engineer",
        agent_key=ENGINEER_AGENT_KEY,
        state_key=ENGINEER_ISSUES_STATE_KEY,
        display_name="Engineer Specialist",
        review_description="バックエンドエンジニアの専門的観点からPRDをレビュー",
    ),
    SpecialistDefinition(
        role="ux_designer",
        agent_key=UX_AGENT_KEY,
        state_key=UX_ISSUES_STATE_KEY,
        display_name="UX Designer Specialist",
        review_description="UXデザイナーの専門的観点からPRDをレビュー",
    ),
    SpecialistDefinition(
        role="qa_tester",
        agent_key=QA_AGENT_KEY,
        state_key=QA_ISSUES_STATE_KEY,
        display_name="QA Tester Specialist",
        review_description="QAテスターの専門的観点からPRDをレビュー",
    ),
    SpecialistDefinition(
        role="pm",
        agent_key=PM_AGENT_KEY,
        state_key=PM_ISSUES_STATE_KEY,
        display_name="PM Specialist",
        review_description="プロダクトマネージャーの専門的観点からPRDをレビュー",
    ),
)

AGENT_STATE_KEYS: Mapping[str, str] = {
    definition.agent_key: definition.state_key for definition in SPECIALIST_DEFINITIONS
}

AGENT_DISPLAY_NAMES: Mapping[str, str] = {
    definition.agent_key: definition.display_name for definition in SPECIALIST_DEFINITIONS
}

STATE_KEY_TO_AGENT_KEY: Mapping[str, str] = {
    definition.state_key: definition.agent_key for definition in SPECIALIST_DEFINITIONS
}

ROLE_TO_DEFINITION: Mapping[str, SpecialistDefinition] = {
    definition.role: definition for definition in SPECIALIST_DEFINITIONS
}

SPECIALIST_AGENT_KEYS: tuple[str, ...] = tuple(definition.agent_key for definition in SPECIALIST_DEFINITIONS)
