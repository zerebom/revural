"""Parallel Orchestrator that aggregates specialist issues into FinalIssue list."""

from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent, ParallelAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.tools.tool_context import ToolContext
from google.genai import types as genai_types

from hibikasu_agent.agents.parallel_orchestrator.tools import (
    AGGREGATE_FINAL_ISSUES_TOOL,
)
from hibikasu_agent.agents.specialist import (
    create_role_agents,
    create_specialists_from_config,
)
from hibikasu_agent.constants.agents import SPECIALIST_DEFINITIONS


class FinalIssuesAggregatorAgent(BaseAgent):
    """Deterministic agent that aggregates specialist outputs without LLM calls."""

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        event_actions = EventActions()

        # Reuse the existing aggregation tool within a ToolContext for state access.
        tool_context = ToolContext(invocation_context=ctx, event_actions=event_actions)
        result = AGGREGATE_FINAL_ISSUES_TOOL(tool_context)
        result_dict = result.model_dump()

        # Ensure downstream consumers observe the aggregated issues in both state and event.
        event_actions.state_delta["final_review_issues"] = result_dict
        event_actions.skip_summarization = True
        event_actions.escalate = True

        issue_count = len(result.final_issues)
        content = genai_types.Content(
            role=self.name,
            parts=[genai_types.Part(text=f"Aggregated {issue_count} final issues")],
        )
        yield Event(author=self.name, content=content, actions=event_actions)


def create_parallel_review_agent(
    model: str = "gemini-2.5-flash", *, selected_agents: list[str] | None = None
) -> SequentialAgent:
    """Build the review workflow agent using a sequential pipeline based on ADK best practices.

    Args:
        model: The LLM model to use for all agents
        selected_agents: Optional list of agent roles to include. If None, all agents are used.
                        Valid roles: "engineer", "ux_designer", "qa_tester", "pm"

    Flow:
    1) Four specialist review agents run concurrently via ParallelAgent and
       persist their typed IssuesResponse into session state using `output_key`.
    2) A deterministic aggregator agent invokes the aggregate_final_issues tool
       and emits the final structured review result without additional LLM calls.
    """

    # Filter definitions based on selected agents
    if selected_agents is not None:
        filtered_definitions = [
            definition for definition in SPECIALIST_DEFINITIONS if definition.role in selected_agents
        ]
        if not filtered_definitions:
            raise ValueError(f"No valid agents found for roles: {selected_agents}")
    else:
        filtered_definitions = list(SPECIALIST_DEFINITIONS)

    # 1) Specialists with explicit output keys defined via shared config
    review_agents = create_specialists_from_config(
        filtered_definitions,
        model=model,
    )

    # 2) Run all specialists concurrently; their structured outputs persist via output_key.
    specialists_parallel = ParallelAgent(
        name="ParallelSpecialists",
        sub_agents=review_agents,
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

    # Create chat specialists from shared config
    chat_agents = []
    for definition in SPECIALIST_DEFINITIONS:
        _, chat_agent = create_role_agents(
            definition.role,
            model=model,
            review_output_key=definition.state_key,
            name_prefix=definition.role,
        )
        chat_agents.append(chat_agent)

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
        sub_agents=chat_agents,
    )

    return coordinator


root_agent = create_parallel_review_agent(model="gemini-2.5-flash")
