"""Parallel Orchestrator that aggregates specialist issues into FinalIssue list."""

from google.adk.agents import BaseAgent, LlmAgent, ParallelAgent, SequentialAgent
from google.adk.events import Event, EventActions
from google.adk.tools.tool_context import ToolContext
from google.genai import types as genai_types

from hibikasu_agent.agents.parallel_orchestrator.tools import (
    AGGREGATE_FINAL_ISSUES_TOOL,
)
from hibikasu_agent.agents.specialist import (
    create_role_agents,
    create_specialist_from_role,
)
from hibikasu_agent.constants.agents import (
    ENGINEER_AGENT_KEY,
    ENGINEER_ISSUES_STATE_KEY,
    PM_AGENT_KEY,
    PM_ISSUES_STATE_KEY,
    QA_AGENT_KEY,
    QA_ISSUES_STATE_KEY,
    UX_AGENT_KEY,
    UX_ISSUES_STATE_KEY,
)


class FinalIssuesAggregatorAgent(BaseAgent):
    """Deterministic agent that aggregates specialist outputs without LLM calls."""

    async def _run_async_impl(self, ctx):  # type: ignore[override]
        event_actions = EventActions()

        # Reuse the existing aggregation tool within a ToolContext for state access.
        tool_context = ToolContext(invocation_context=ctx, event_actions=event_actions)
        result = AGGREGATE_FINAL_ISSUES_TOOL(tool_context)

        # Ensure downstream consumers observe the aggregated issues in both state and event.
        event_actions.state_delta["final_review_issues"] = result
        event_actions.skip_summarization = True
        event_actions.escalate = True

        issue_count = len(result.get("final_issues", [])) if isinstance(result, dict) else 0
        content = genai_types.Content(
            role=self.name,
            parts=[genai_types.Part(text=f"Aggregated {issue_count} final issues")],
        )
        yield Event(author=self.name, content=content, actions=event_actions)


def create_parallel_review_agent(model: str = "gemini-2.5-flash") -> SequentialAgent:
    """Build the review workflow agent using a sequential pipeline based on ADK best practices.

    Flow:
    1) Four specialist review agents run concurrently via ParallelAgent and
       persist their typed IssuesResponse into session state using `output_key`.
    2) A deterministic aggregator agent invokes the aggregate_final_issues tool
       and emits the final structured review result without additional LLM calls.
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

    # 2) Run all specialists concurrently; their structured outputs persist via output_key.
    specialists_parallel = ParallelAgent(
        name="ParallelSpecialists",
        sub_agents=[engineer, ux, qa, pm],
        description="Executes specialist reviews concurrently.",
    )

    merger = FinalIssuesAggregatorAgent(
        name="IssueAggregatorMerger",
        description="Aggregates specialist outputs deterministically.",
    )

    # 5) Combine them in a SequentialAgent pipeline
    pipeline = SequentialAgent(
        name="ReviewPipelineWithTools",
        sub_agents=[specialists_parallel, merger],
        description=("Coordinates specialist agents in parallel and deterministic aggregation."),
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
