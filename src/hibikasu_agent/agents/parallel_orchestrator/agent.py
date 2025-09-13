"""Parallel Orchestrator that aggregates specialist issues into FinalIssue list.

This agent orchestrates four specialist agents via AgentTool with summarization
disabled, then aggregates their typed outputs into FinalIssuesResponse.
"""

from typing import cast

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import AgentTool, FunctionTool
from pydantic import BaseModel as PydanticBaseModel

from hibikasu_agent.agents.parallel_orchestrator.tools import (
    aggregate_final_issues,
)
from hibikasu_agent.agents.specialist import (
    create_role_agents,
    create_specialist_from_role,
)
from hibikasu_agent.schemas.models import FinalIssuesResponse


def create_parallel_review_agent(model: str = "gemini-2.5-flash") -> SequentialAgent:
    """Build the review workflow agent using AgentTools.

    Flow:
    1) A controller LlmAgent calls four specialist AgentTools, each returning
       IssuesResponse as a typed object (skip_summarization=True).
    2) The controller then invokes the aggregate_final_issues tool to produce
       a FinalIssuesResponse and stores it under "final_review_issues".
    """

    # 1) Specialists with explicit output keys
    engineer = create_specialist_from_role(
        "engineer",
        name="engineer_specialist",
        description="バックエンドエンジニアの専門的観点からPRDをレビュー",
        model=model,
        output_key="engineer_issues",
    )

    ux = create_specialist_from_role(
        "ux_designer",
        name="ux_designer_specialist",
        description="UXデザイナーの専門的観点からPRDをレビュー",
        model=model,
        output_key="ux_designer_issues",
    )

    qa = create_specialist_from_role(
        "qa_tester",
        name="qa_tester_specialist",
        description="QAテスターの専門的観点からPRDをレビュー",
        model=model,
        output_key="qa_tester_issues",
    )

    pm = create_specialist_from_role(
        "pm",
        name="pm_specialist",
        description="プロダクトマネージャーの専門的観点からPRDをレビュー",
        model=model,
        output_key="pm_issues",
    )

    # 1.5) Wrap specialists as AgentTools with summarization disabled
    engineer_tool = AgentTool(agent=engineer, skip_summarization=True)
    ux_tool = AgentTool(agent=ux, skip_summarization=True)
    qa_tool = AgentTool(agent=qa, skip_summarization=True)
    pm_tool = AgentTool(agent=pm, skip_summarization=True)

    # 2) Aggregation tool
    aggregate_tool = FunctionTool(aggregate_final_issues)

    # Controller LlmAgent: calls four tools then aggregates
    controller = LlmAgent(
        name="SpecialistToolOrchestrator",
        model=model,
        description=("Invokes four specialist AgentTools and aggregates their typed outputs."),
        instruction=(
            "あなたはレビュー統合責任者です。次の手順で必ずツールを呼び出してください。\n"
            "1) engineer_specialist, ux_designer_specialist, qa_tester_specialist, pm_specialist の各ツールを呼び出し、"
            "IssuesResponse を取得します。\n"
            "2) aggregate_final_issues ツールを呼び出し、引数は次を指定します。\n"
            "   - prd_text: 会話の入力（完全なPRD本文）\n"
            "   - engineer_issues: 1) で得たエンジニアの IssuesResponse\n"
            "   - ux_designer_issues: 1) で得たUXデザイナーの IssuesResponse\n"
            "   - qa_tester_issues: 1) で得たQAテスターの IssuesResponse\n"
            "   - pm_issues: 1) で得たPMの IssuesResponse\n"
            "3) ツールの戻り値（FinalIssuesResponse）のみを最終出力として返します。テキスト要約はしないでください。"
        ),
        tools=[engineer_tool, ux_tool, qa_tool, pm_tool, aggregate_tool],
        output_schema=cast(type[PydanticBaseModel], FinalIssuesResponse),
        output_key="final_review_issues",
    )

    pipeline = SequentialAgent(
        name="ReviewPipelineWithTools",
        sub_agents=[controller],
        description=("Coordinates specialist AgentTools and deterministic aggregation."),
    )

    return pipeline


# Export a default root agent for optional discovery/use


def create_coordinator_agent(model: str = "gemini-2.5-flash") -> LlmAgent:
    """Coordinator that routes by free-text to specialist chat agents.

    Decoupled from the review pipeline. Uses LLM-driven delegation (transfer_to_agent)
    to move the conversation to the most suitable specialist based on the user's text.
    """

    # Create chat specialists
    _, eng_chat = create_role_agents(
        "engineer",
        model=model,
        review_output_key="engineer_issues",
        name_prefix="engineer",
    )
    _, ux_chat = create_role_agents(
        "ux_designer",
        model=model,
        review_output_key="ux_designer_issues",
        name_prefix="ux_designer",
    )
    _, qa_chat = create_role_agents(
        "qa_tester",
        model=model,
        review_output_key="qa_tester_issues",
        name_prefix="qa_tester",
    )
    _, pm_chat = create_role_agents("pm", model=model, review_output_key="pm_issues", name_prefix="pm")

    coordinator = LlmAgent(
        name="Coordinator",
        model=model,
        description="Routes incoming issue text to the best specialist chat agent.",
        instruction=(
            "あなたは司令塔エージェントです。ユーザーの課題/質問のテキストを読み、\n"
            "最も適切な専門家（engineer_chat / ux_designer_chat / "
            "qa_tester_chat / pm_chat）へ\n"
            "transfer_to_agent(agent_name=...) を用いて会話を移譲してください。\n"
            "- 技術設計・実装・パフォーマンス・セキュリティ → engineer_chat\n"
            "- UX・UI・ユーザーフロー・情報設計 → ux_designer_chat\n"
            "- テスト観点・品質リスク・再現手順 → qa_tester_chat\n"
            "- 企画・優先度・ステークホルダー調整・KPI → pm_chat\n"
            "曖昧な場合は短く確認の質問をしてから転送先を決定してください。\n"
        ),
        sub_agents=[eng_chat, ux_chat, qa_chat, pm_chat],
    )

    return coordinator


root_agent = create_coordinator_agent(model="gemini-2.5-flash")
