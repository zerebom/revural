from __future__ import annotations

from types import SimpleNamespace

import pytest
from hibikasu_agent.agents.parallel_orchestrator.tools import (
    AGGREGATE_FINAL_ISSUES_TOOL,
    _load_issues_from_state,
    _to_final_issues,
)
from hibikasu_agent.constants.agents import AGENT_STATE_KEYS, SPECIALIST_DEFINITIONS
from hibikasu_agent.schemas.models import FinalIssuesResponse, IssueItem, IssuesResponse
from pydantic import ValidationError


def test_load_issues_from_state_raises_on_malformed_dict() -> None:
    """Malformed payloads must surface a ValidationError."""

    malformed = {"engineer_issues": {"bad_key": "value"}}

    with pytest.raises(ValidationError):
        _load_issues_from_state(malformed, "engineer_issues")


def test_to_final_issues_preserves_original_text() -> None:
    """Ensure original_text is kept intact (no backend truncation)."""

    long_text = "a" * 200
    issues = IssuesResponse(issues=[IssueItem(severity="High", comment="c", original_text=long_text)])

    final_issues = _to_final_issues("engineer_specialist", issues)

    assert len(final_issues) == 1
    assert final_issues[0].original_text == long_text


def _make_issue_item(severity: str, comment: str) -> IssueItem:
    return IssueItem(severity=severity, comment=comment, original_text=f"orig:{comment}")


def test_aggregate_final_issues_orders_by_severity() -> None:
    """Aggregated issues must be sorted by severity with sequential priorities."""

    state: dict[str, object] = {}
    # Only use the first two definitions for brevity
    definitions = SPECIALIST_DEFINITIONS[:2]
    for definition in definitions:
        state_key = AGENT_STATE_KEYS[definition.agent_key]
        issues = IssuesResponse(
            issues=[
                _make_issue_item("Low", f"low-{definition.role}"),
                _make_issue_item("High", f"high-{definition.role}"),
            ]
        )
        state[state_key] = issues

    tool_context = SimpleNamespace(state=state)

    response = AGGREGATE_FINAL_ISSUES_TOOL(tool_context)
    assert isinstance(response, FinalIssuesResponse)

    final_issues = response.final_issues
    assert len(final_issues) == len(definitions) * 2
    # High severity items should come first, followed by Low
    severities = [issue.severity for issue in final_issues]
    assert severities[: len(definitions)] == ["High"] * len(definitions)
    assert severities[len(definitions) :] == ["Low"] * len(definitions)
    # Priority should be sequential starting at 1
    assert [issue.priority for issue in final_issues] == list(range(1, len(final_issues) + 1))


def test_aggregate_final_issues_handles_missing_state() -> None:
    """Absent specialist state entries should yield an empty result without error."""

    tool_context = SimpleNamespace(state={})

    response = AGGREGATE_FINAL_ISSUES_TOOL(tool_context)
    assert isinstance(response, FinalIssuesResponse)
    assert response.final_issues == []
