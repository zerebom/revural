"""Parallel Orchestrator that aggregates specialist issues into FinalIssue list.

This agent runs four specialist LlmAgents concurrently via ParallelAgent,
then merges their structured outputs using a tool into FinalIssuesResponse.
"""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import FunctionTool

from hibikasu_agent.agents.parallel_orchestrator.tools import (
    aggregate_final_issues,
)
from hibikasu_agent.agents.specialist import (
    IssuesResponse,
    create_specialist_from_role,
)
from hibikasu_agent.schemas.models import FinalIssuesResponse


def create_parallel_review_agent(model: str = "gemini-2.5-flash") -> SequentialAgent:
    """Build the parallel review workflow agent.

    Flow:
    1) ParallelAgent runs 4 specialists concurrently, each producing IssuesResponse
       and storing it under a dedicated output_key in session state.
    2) Merger LlmAgent invokes a tool to aggregate these into FinalIssuesResponse.
    """

    # 1) Specialists with explicit output keys
    engineer = create_specialist_from_role(
        "engineer",
        name="engineer_specialist",
        description="バックエンドエンジニアの専門的観点からPRDをレビュー",
        model=model,
        output_schema=IssuesResponse,
        output_key="engineer_issues",
    )

    ux = create_specialist_from_role(
        "ux_designer",
        name="ux_designer_specialist",
        description="UXデザイナーの専門的観点からPRDをレビュー",
        model=model,
        output_schema=IssuesResponse,
        output_key="ux_designer_issues",
    )

    qa = create_specialist_from_role(
        "qa_tester",
        name="qa_tester_specialist",
        description="QAテスターの専門的観点からPRDをレビュー",
        model=model,
        output_schema=IssuesResponse,
        output_key="qa_tester_issues",
    )

    pm = create_specialist_from_role(
        "pm",
        name="pm_specialist",
        description="プロダクトマネージャーの専門的観点からPRDをレビュー",
        model=model,
        output_schema=IssuesResponse,
        output_key="pm_issues",
    )

    parallel = ParallelAgent(
        name="ParallelSpecialistReview",
        sub_agents=[engineer, ux, qa, pm],
        description="Runs four specialists in parallel to generate issue lists.",
    )

    # 2) Aggregation tool and merger agent
    aggregate_tool = FunctionTool(aggregate_final_issues)

    merger = LlmAgent(
        name="IssueAggregatorMerger",
        model=model,
        description=(
            "Aggregates parallel specialist outputs into a prioritized final list."
        ),
        instruction=(
            "あなたはレビュー統合責任者です。\n"
            "提供された4人の専門家のレビュー結果を、必ずaggregate_final_issuesツールを使って統合してください。\n\n"
            "引数は次の通りです。\n"
            "- prd_text: 会話の入力（完全なPRD本文）\n"
            "- engineer_issues: {engineer_issues}\n"
            "- ux_designer_issues: {ux_designer_issues}\n"
            "- qa_tester_issues: {qa_tester_issues}\n"
            "- pm_issues: {pm_issues}\n\n"
            "出力はツールの戻り値（FinalIssuesResponse）のみを返してください。"
        ),
        tools=[aggregate_tool],
        output_schema=FinalIssuesResponse,
    )

    pipeline = SequentialAgent(
        name="ParallelReviewAndAggregatePipeline",
        sub_agents=[parallel, merger],
        description=(
            "Coordinates parallel specialist review and deterministic aggregation."
        ),
    )

    return pipeline


# Export a default root agent for optional discovery/use
root_agent = create_parallel_review_agent(model="gemini-2.5-flash")
