"""Tools for the Parallel Orchestrator workflow."""

from typing import Any
from uuid import uuid4

from google.adk.tools.tool_context import ToolContext
from pydantic import ValidationError

from hibikasu_agent.constants.agents import (
    AGENT_DISPLAY_NAMES,
    AGENT_STATE_KEYS,
    SPECIALIST_DEFINITIONS,
)
from hibikasu_agent.schemas.models import (
    FinalIssue,
    FinalIssuesResponse,
    IssueItem,
    IssuesResponse,
)
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


MAX_ISSUES_PER_AGENT = 5


def _to_final_issues(agent_key: str, issues_resp: IssuesResponse) -> list[FinalIssue]:
    """Convert a typed IssuesResponse to FinalIssue items for a given agent."""
    final_items: list[FinalIssue] = []
    items = issues_resp.issues[:MAX_ISSUES_PER_AGENT]
    for item in items:
        parsed: IssueItem = item

        final_items.append(
            FinalIssue(
                issue_id=str(uuid4()),
                priority=parsed.priority,
                agent_name=AGENT_DISPLAY_NAMES.get(agent_key, agent_key),
                comment=parsed.comment,
                original_text=parsed.original_text,
            )
        )
    return final_items


def _load_issues_from_state(state: dict[str, Any], key: str) -> IssuesResponse:
    raw = state.get(key)
    if isinstance(raw, IssuesResponse):
        return raw
    if isinstance(raw, dict):
        try:
            return IssuesResponse.model_validate(raw)
        except ValidationError:
            logger.error("Failed to parse issues for %s", key, exc_info=True)
            raise
    if raw is None:
        return IssuesResponse(issues=[])
    logger.error("Unexpected state payload for %s: %r", key, type(raw))
    raise TypeError(f"Unexpected state payload type for {key}: {type(raw)!r}")


def _calculate_issue_priorities(issues: list[FinalIssue]) -> list[FinalIssue]:
    """Order issues by their priority (already normalized to 1/2/3)."""

    return sorted(issues, key=lambda item: item.priority)


def aggregate_final_issues(tool_context: ToolContext) -> FinalIssuesResponse:
    """Aggregate specialist outputs stored in state and return a typed response."""

    state = getattr(tool_context, "state", {}) or {}

    final_items: list[FinalIssue] = []
    for definition in SPECIALIST_DEFINITIONS:
        issues = _load_issues_from_state(state, AGENT_STATE_KEYS[definition.agent_key])
        final_items.extend(_to_final_issues(definition.agent_key, issues))

    prioritized = _calculate_issue_priorities(final_items)
    response = FinalIssuesResponse(final_issues=prioritized)
    logger.info("Aggregated final issues", count=len(prioritized))
    return response


AGGREGATE_FINAL_ISSUES_TOOL = aggregate_final_issues
