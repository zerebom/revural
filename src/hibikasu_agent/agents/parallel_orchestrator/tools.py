"""Tools for the Parallel Orchestrator workflow."""

from typing import Any
from uuid import uuid4

from google.adk.tools.tool_context import ToolContext
from pydantic import ValidationError

from hibikasu_agent.constants.agents import (
    AGENT_DISPLAY_NAMES,
    AGENT_STATE_KEYS,
    ENGINEER_AGENT_KEY,
    PM_AGENT_KEY,
    QA_AGENT_KEY,
    UX_AGENT_KEY,
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
        # Items are already IssueItem; normalize severity and map
        parsed: IssueItem = item
        final_items.append(
            FinalIssue(
                issue_id=str(uuid4()),
                priority=0,  # set later
                agent_name=AGENT_DISPLAY_NAMES.get(agent_key, agent_key),
                severity=parsed.normalize_severity(),
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


def aggregate_final_issues(tool_context: ToolContext) -> dict[str, Any]:
    """Aggregate specialist outputs stored in state and return a serializable payload."""

    state = getattr(tool_context, "state", {}) or {}

    engineer = _load_issues_from_state(state, AGENT_STATE_KEYS[ENGINEER_AGENT_KEY])
    ux = _load_issues_from_state(state, AGENT_STATE_KEYS[UX_AGENT_KEY])
    qa = _load_issues_from_state(state, AGENT_STATE_KEYS[QA_AGENT_KEY])
    pm = _load_issues_from_state(state, AGENT_STATE_KEYS[PM_AGENT_KEY])

    final_items: list[FinalIssue] = []
    final_items.extend(_to_final_issues(ENGINEER_AGENT_KEY, engineer))
    final_items.extend(_to_final_issues(UX_AGENT_KEY, ux))
    final_items.extend(_to_final_issues(QA_AGENT_KEY, qa))
    final_items.extend(_to_final_issues(PM_AGENT_KEY, pm))

    severity_order = {"High": 0, "Mid": 1, "Low": 2}
    final_items.sort(key=lambda item: severity_order.get(item.severity, 3))
    for idx, issue in enumerate(final_items, start=1):
        issue.priority = idx

    response = FinalIssuesResponse(final_issues=final_items)
    response_dict = response.model_dump()
    # Persist for downstream consumers (ADKService.run_review_async expects this key)
    state["final_review_issues"] = response_dict
    logger.info("Aggregated final issues", count=len(final_items))
    return response_dict


AGGREGATE_FINAL_ISSUES_TOOL = aggregate_final_issues
