"""Agent-related constant definitions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final

ENGINEER_AGENT_KEY: Final[str] = "engineer_specialist"
UX_AGENT_KEY: Final[str] = "ux_designer_specialist"
QA_AGENT_KEY: Final[str] = "qa_tester_specialist"
PM_AGENT_KEY: Final[str] = "pm_specialist"

ENGINEER_ISSUES_STATE_KEY: Final[str] = "engineer_issues"
UX_ISSUES_STATE_KEY: Final[str] = "ux_designer_issues"
QA_ISSUES_STATE_KEY: Final[str] = "qa_tester_issues"
PM_ISSUES_STATE_KEY: Final[str] = "pm_issues"

AGENT_STATE_KEYS: Mapping[str, str] = {
    ENGINEER_AGENT_KEY: ENGINEER_ISSUES_STATE_KEY,
    UX_AGENT_KEY: UX_ISSUES_STATE_KEY,
    QA_AGENT_KEY: QA_ISSUES_STATE_KEY,
    PM_AGENT_KEY: PM_ISSUES_STATE_KEY,
}

AGENT_DISPLAY_NAMES: Mapping[str, str] = {
    ENGINEER_AGENT_KEY: "Engineer Specialist",
    UX_AGENT_KEY: "UX Designer Specialist",
    QA_AGENT_KEY: "QA Tester Specialist",
    PM_AGENT_KEY: "PM Specialist",
}

SPECIALIST_AGENT_KEYS: tuple[str, ...] = tuple(AGENT_STATE_KEYS.keys())
