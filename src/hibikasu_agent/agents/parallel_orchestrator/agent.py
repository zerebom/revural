"""Parallel Orchestrator that aggregates specialist issues into FinalIssue list.

This agent orchestrates four specialist agents via AgentTool with summarization
disabled, then aggregates their typed outputs into FinalIssuesResponse.
"""

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import AgentTool, FunctionTool

from hibikasu_agent.agents.parallel_orchestrator.tools import AGGREGATE_FINAL_ISSUES_TOOL
from hibikasu_agent.agents.specialist import (
    create_role_agents,
    create_specialist_from_role,
)
from hibikasu_agent.constants import (
    ENGINEER_AGENT_KEY,
    ENGINEER_ISSUES_STATE_KEY,
    PM_AGENT_KEY,
    PM_ISSUES_STATE_KEY,
    QA_AGENT_KEY,
    QA_ISSUES_STATE_KEY,
    UX_AGENT_KEY,
    UX_ISSUES_STATE_KEY,
)
from hibikasu_agent.schemas.models import FinalIssuesResponse


def create_parallel_review_agent(model: str = "gemini-2.5-flash") -> SequentialAgent:
    """Build the review workflow agent using a sequential pipeline based on ADK best practices.

    Flow:
    1) SpecialistRunner agent calls four specialist AgentTools. Their typed
       outputs (IssuesResponse) are stored in session state via their `output_key`.
    2) IssueAggregatorMerger agent invokes the aggregate_final_issues tool,
       which reads from state by referencing state keys (e.g., `{engineer_issues}`)
       in its instruction, and produces the final FinalIssuesResponse.
    """

    # 1) Specialists with explicit output keys
    engineer = create_specialist_from_role(
        "engineer",
        name=ENGINEER_AGENT_KEY,
        description="バックエンドエンジニアの専門的観点からPRDをレビュー",
        model=model,
        output_key=ENGINEER_ISSUES_STATE_KEY,
    )

    ux = create_specialist_from_role(
        "ux_designer",
        name=UX_AGENT_KEY,
        description="UXデザイナーの専門的観点からPRDをレビュー",
        model=model,
        output_key=UX_ISSUES_STATE_KEY,
    )

    qa = create_specialist_from_role(
        "qa_tester",
        name=QA_AGENT_KEY,
        description="QAテスターの専門的観点からPRDをレビュー",
        model=model,
        output_key=QA_ISSUES_STATE_KEY,
    )

    pm = create_specialist_from_role(
        "pm",
        name=PM_AGENT_KEY,
        description="プロダクトマネージャーの専門的観点からPRDをレビュー",
        model=model,
        output_key=PM_ISSUES_STATE_KEY,
    )

    # 2) Wrap specialists as AgentTools with summarization disabled
    engineer_tool = AgentTool(agent=engineer, skip_summarization=True)
    ux_tool = AgentTool(agent=ux, skip_summarization=True)
    qa_tool = AgentTool(agent=qa, skip_summarization=True)
    pm_tool = AgentTool(agent=pm, skip_summarization=True)

    # 3) Step 1 Agent: Runs the four specialist tools.
    # The output of each tool is automatically saved to the state under its `output_key`.
    specialist_runner = LlmAgent(
        name="SpecialistRunner",
        model=model,
        description="Runs four specialist tools.",
        instruction=(
            "You must call all four of the following tools using the user's input: "
            f"`{ENGINEER_AGENT_KEY}`, `{UX_AGENT_KEY}`, "
            f"`{QA_AGENT_KEY}`, `{PM_AGENT_KEY}`."
        ),
        tools=[engineer_tool, ux_tool, qa_tool, pm_tool],
    )

    aggregate_tool = FunctionTool(func=AGGREGATE_FINAL_ISSUES_TOOL)

    merger = LlmAgent(
        name="IssueAggregatorMerger",
        model=model,
        description="Calls a deterministic tool to aggregate specialist outputs.",
        instruction=(
            "Call the `aggregate_final_issues` tool exactly once with no arguments. "
            "Do not rewrite or summarize issues manually. Return the tool result as-is."
        ),
        tools=[aggregate_tool],
        output_schema=FinalIssuesResponse,
        output_key="final_review_issues",
    )

    # 5) Combine them in a SequentialAgent pipeline
    pipeline = SequentialAgent(
        name="ReviewPipelineWithTools",
        sub_agents=[specialist_runner, merger],
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


root_agent = create_parallel_review_agent(model="gemini-2.5-flash")
