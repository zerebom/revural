"""Tools for the orchestrator agent."""

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from hibikasu_agent.schemas.models import Issue, ReviewSession
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


class SpecialistIssue(BaseModel):
    """Model for individual issue from specialist agent."""

    severity: str = Field(pattern="^(High|Mid|Low|Medium)$")
    description: str = Field(min_length=1)
    recommendation: str = Field(default="")
    category: str = Field(default="")

    def normalize_severity(self) -> str:
        """Normalize severity values."""
        return "Mid" if self.severity == "Medium" else self.severity


def structure_review_results(
    prd_text: str,
    engineer_issues: list[dict],
    ux_designer_issues: list[dict],
    qa_tester_issues: list[dict],
    pm_issues: list[dict],
) -> dict[str, Any]:
    """Structure review results from specialist agents into unified format.

    This version handles structured data directly from sub_agents
    instead of JSON strings.

    Args:
        prd_text: The full PRD text being reviewed
        engineer_issues: List of issue dicts from engineer specialist
        ux_designer_issues: List of issue dicts from UX designer specialist
        qa_tester_issues: List of issue dicts from QA tester specialist
        pm_issues: List of issue dicts from PM specialist

    Returns:
        Dictionary representation of ReviewSession with all structured issues
    """
    logger.info("Starting to structure review results from structured data")

    all_issues: list[Issue] = []

    # Map agent names to their structured issues
    agent_issues = {
        "engineer": engineer_issues,
        "ux_designer": ux_designer_issues,
        "qa_tester": qa_tester_issues,
        "pm": pm_issues,
    }

    # Process each specialist's structured issues
    for agent_name, issues_data in agent_issues.items():
        try:
            # issues_data should already be a list of dicts
            if not isinstance(issues_data, list):
                logger.warning(
                    f"Expected list from {agent_name}, got {type(issues_data)}"
                )
                continue

            # Use Pydantic to validate and parse each issue
            for issue_data in issues_data:
                try:
                    # Validate with Pydantic model
                    specialist_issue = SpecialistIssue(**issue_data)

                    # Create Issue object from validated data
                    issue = Issue(
                        issue_id=str(uuid4()),
                        priority=0,  # Will be set later based on severity
                        agent_name=agent_name,
                        agent_avatar=f"{agent_name}_icon",
                        severity=specialist_issue.normalize_severity(),
                        comment=specialist_issue.description,
                        original_text=specialist_issue.recommendation,
                    )
                    all_issues.append(issue)

                except Exception as e:
                    logger.warning(
                        f"Invalid issue format from {agent_name}: {e}. "
                        f"Data: {issue_data}"
                    )
                    continue

        except Exception as e:
            logger.error(f"Error processing {agent_name} issues: {e}")
            continue

    # Calculate priorities based on severity
    # Sort by severity (High -> Mid -> Low) and assign priorities
    severity_order = {"High": 0, "Mid": 1, "Low": 2}
    all_issues.sort(key=lambda x: severity_order.get(x.severity, 3))

    # Assign priority numbers (1 is highest priority)
    for idx, issue in enumerate(all_issues):
        issue.priority = idx + 1

    logger.info(f"Structured {len(all_issues)} total issues")

    # Create ReviewSession
    review_session = ReviewSession(
        prd_text=prd_text,
        panel_type="Webサービス",
        final_issues=all_issues,
    )

    # Return as dictionary
    result = review_session.model_dump()
    logger.info(f"Created ReviewSession with ID: {result['review_id']}")

    return result
