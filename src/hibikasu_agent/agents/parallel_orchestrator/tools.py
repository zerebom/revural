"""Tools for the Parallel Orchestrator workflow."""

from typing import Any, cast
from uuid import uuid4

from hibikasu_agent.schemas.models import FinalIssue, FinalIssuesResponse, IssueItem
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


def _extract_list(value: Any) -> list[dict[str, Any]]:
    """Extract list[dict] of issues from various possible shapes.

    Accepts:
    - list[dict]
    - dict with key "issues"
    - pydantic model with attribute "issues"
    - str containing JSON (with or without markdown code block)
    - None or unexpected -> returns []
    """
    if value is None:
        return []

    # If value is a string, skip processing (not supported without JSON parsing)
    if isinstance(value, str):
        return []

    # Already a list of dicts
    if isinstance(value, list):
        return cast("list[dict[str, Any]]", value)
    # Pydantic model or object with attribute
    issues_attr = getattr(value, "issues", None)
    if issues_attr is not None:
        return cast("list[dict[str, Any]]", issues_attr) if isinstance(issues_attr, list) else []
    # Dict with key
    if isinstance(value, dict) and isinstance(value.get("issues"), list):
        return cast("list[dict[str, Any]]", value["issues"])
    return []


def aggregate_final_issues(
    prd_text: str,
    engineer_issues: Any,
    ux_designer_issues: Any,
    qa_tester_issues: Any,
    pm_issues: Any,
) -> dict[str, Any]:
    """Aggregate specialist issues and return prioritized FinalIssuesResponse.

    Returns a dict compatible with FinalIssuesResponse.model_dump().
    """
    logger.info("Aggregating specialist issues into FinalIssue list")

    issues_by_agent: dict[str, list[dict[str, Any]]] = {
        "engineer": _extract_list(engineer_issues),
        "ux_designer": _extract_list(ux_designer_issues),
        "qa_tester": _extract_list(qa_tester_issues),
        "pm": _extract_list(pm_issues),
    }

    final_items: list[FinalIssue] = []

    for agent_name, items in issues_by_agent.items():
        for raw in items:
            try:
                parsed = IssueItem(**raw)
            except Exception as e:  # validation error
                logger.warning(
                    "Skipping invalid issue from %s: %s | data=%s",
                    agent_name,
                    e,
                    raw,
                )
                continue

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

    # Priority by severity order (stable within same severity)
    severity_order = {"High": 0, "Mid": 1, "Low": 2}
    final_items.sort(key=lambda x: severity_order.get(x.severity, 3))
    for idx, item in enumerate(final_items, start=1):
        item.priority = idx

    resp = FinalIssuesResponse(final_issues=final_items)
    logger.info(f"Created {len(final_items)} final issues")
    result: dict[str, Any] = resp.model_dump()
    return result
