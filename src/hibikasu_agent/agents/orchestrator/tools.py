"""Tools for the orchestrator agent."""

import json
from typing import Any
from uuid import uuid4

from hibikasu_agent.schemas.models import Issue, ReviewSession
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


def structure_review_results(
    prd_text: str,
    engineer_review: str,
    ux_designer_review: str,
    qa_tester_review: str,
    pm_review: str,
) -> dict[str, Any]:
    """Structure review results from all specialists into a unified format.

    This tool takes the raw review outputs from each specialist agent and
    structures them into a ReviewSession model with prioritized issues.

    Args:
        prd_text: The full PRD text being reviewed
        engineer_review: JSON string from engineer specialist
        ux_designer_review: JSON string from UX designer specialist
        qa_tester_review: JSON string from QA tester specialist
        pm_review: JSON string from PM specialist

    Returns:
        Dictionary representation of ReviewSession with all structured issues
    """
    logger.info("Starting to structure review results")

    all_issues: list[Issue] = []

    # Map agent names to their reviews
    agent_reviews = {
        "engineer": engineer_review,
        "ux_designer": ux_designer_review,
        "qa_tester": qa_tester_review,
        "pm": pm_review,
    }

    # Parse each specialist's review and create Issue objects
    for agent_name, review_json in agent_reviews.items():
        try:
            # Parse the JSON response
            review_data = json.loads(review_json)

            # Extract issues from the review
            # Assuming each specialist returns an array of issues
            if isinstance(review_data, list):
                issues = review_data
            elif isinstance(review_data, dict) and "issues" in review_data:
                issues = review_data["issues"]
            else:
                logger.warning(
                    f"Unexpected format from {agent_name}: {type(review_data)}"
                )
                continue

            # Create Issue objects
            for _, issue_data in enumerate(issues):
                issue = Issue(
                    issue_id=str(uuid4()),
                    priority=0,  # Will be set later based on severity
                    agent_name=agent_name,
                    agent_avatar=f"{agent_name}_icon",  # Simple avatar identifier
                    severity=issue_data.get("severity", "Mid"),
                    comment=issue_data.get("comment", ""),
                    original_text=issue_data.get("original_text", ""),
                )
                all_issues.append(issue)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {agent_name}: {e}")
            continue
        except Exception as e:
            logger.error(f"Error processing {agent_name} review: {e}")
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
        panel_type="Webサービス",  # Default panel type
        final_issues=all_issues,
    )

    # Return as dictionary (not JSON string)
    result = review_session.model_dump()
    logger.info(f"Created ReviewSession with ID: {result['review_id']}")

    return result
