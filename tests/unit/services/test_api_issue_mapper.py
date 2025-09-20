from __future__ import annotations

from hibikasu_agent.api.schemas.reviews import Issue as ApiIssue
from hibikasu_agent.services.mappers.api_issue_mapper import map_api_issue


def test_map_api_issue_uses_summary_if_present() -> None:
    item = {
        "issue_id": "1",
        "priority": 2,
        "agent_name": "engineer_specialist",
        "summary": "Provided summary",
        "comment": "comment",
        "original_text": "abc",
    }
    issue = map_api_issue(item, "abc")
    assert isinstance(issue, ApiIssue)
    assert issue.summary == "Provided summary"
    assert issue.priority == 2


def test_map_api_issue_derives_summary_from_comment() -> None:
    comment = "First sentence. Second sentence."
    item = {
        "issue_id": "2",
        "priority": "3",
        "agent_name": "pm_specialist",
        "comment": comment,
        "original_text": "abc",
    }
    issue = map_api_issue(item, "abc")
    assert issue.summary.startswith("First sentence")
    assert issue.priority == 3


def test_map_api_issue_handles_missing_priority() -> None:
    item = {
        "issue_id": "3",
        "agent_name": "ux_designer_specialist",
        "comment": "",
        "original_text": "snippet",
    }
    issue = map_api_issue(item, "---snippet---")
    assert issue.priority == 0
    assert issue.summary == "snippet"
    assert issue.span is not None
