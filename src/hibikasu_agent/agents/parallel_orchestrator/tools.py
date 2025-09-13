"""Tools for the Parallel Orchestrator workflow."""

from uuid import uuid4

from hibikasu_agent.schemas.models import (
    FinalIssue,
    FinalIssuesResponse,
    IssueItem,
    IssuesResponse,
)
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


def _to_final_issues(agent_name: str, issues_resp: IssuesResponse) -> list[FinalIssue]:
    """Convert a typed IssuesResponse to FinalIssue items for a given agent."""
    final_items: list[FinalIssue] = []
    for item in issues_resp.issues:
        # Items are already IssueItem; normalize severity and map
        parsed: IssueItem = item
        final_items.append(
            FinalIssue(
                issue_id=str(uuid4()),
                priority=0,  # set later
                agent_name=agent_name,
                severity=parsed.normalize_severity(),
                comment=parsed.comment,
                original_text=parsed.original_text,
            )
        )
    return final_items


def aggregate_final_issues(
    prd_text: str,  # kept for future use/traceability
    engineer_issues: IssuesResponse,
    ux_designer_issues: IssuesResponse,
    qa_tester_issues: IssuesResponse,
    pm_issues: IssuesResponse,
) -> FinalIssuesResponse:
    """Aggregate specialist issues and return prioritized FinalIssuesResponse.

    Inputs and outputs are fully typed Pydantic models to ensure reliability.
    """
    logger.info("Aggregating specialist issues into FinalIssue list (typed)")

    final_items: list[FinalIssue] = []

    final_items.extend(_to_final_issues("engineer", engineer_issues))
    final_items.extend(_to_final_issues("ux_designer", ux_designer_issues))
    final_items.extend(_to_final_issues("qa_tester", qa_tester_issues))
    final_items.extend(_to_final_issues("pm", pm_issues))

    # Priority by severity order (stable within same severity)
    severity_order = {"High": 0, "Mid": 1, "Low": 2}
    final_items.sort(key=lambda x: severity_order.get(x.severity, 3))
    for idx, item in enumerate(final_items, start=1):
        item.priority = idx

    resp = FinalIssuesResponse(final_issues=final_items)
    logger.info(f"Created {len(final_items)} final issues")
    return resp
