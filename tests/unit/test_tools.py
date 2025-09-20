from __future__ import annotations

import pytest
from hibikasu_agent.agents.parallel_orchestrator.tools import (
    _load_issues_from_state,
    _to_final_issues,
)
from hibikasu_agent.schemas.models import IssueItem, IssuesResponse
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
