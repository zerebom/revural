"""Review Orchestrator Agent for ADK Web discovery."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from hibikasu_agent.agents.orchestrator.tools import structure_review_results
from hibikasu_agent.agents.specialist import (
    create_engineer_agent,
    create_pm_agent,
    create_qa_tester_agent,
    create_ux_designer_agent,
)


def create_review_orchestrator_agent(model: str = "gemini-2.5-flash") -> LlmAgent:
    """Create Review Orchestrator Agent using sub_agents pattern."""

    # Create sub-agents for all specialists
    sub_agents = [
        create_engineer_agent(model),
        create_ux_designer_agent(model),
        create_qa_tester_agent(model),
        create_pm_agent(model),
    ]

    # Import and create the structure tool

    structure_tool = FunctionTool(structure_review_results)

    # Create orchestrator agent
    agent = LlmAgent(
        name="review_orchestrator",
        model=model,
        instruction="""
あなたはPRD（Product Requirements Document）レビューの統括責任者です。
4人の専門家（Engineer、UX Designer、QA Tester、PM）にPRDを並行レビューしてもらい、
その結果を統合して最終的なレビューセッションを作成します。

手順：
1. 提供されたPRDを各専門家に送信してレビューを依頼
2. 各専門家から構造化されたレビュー結果を受け取る
3. structure_review_resultsツールを使用して結果を統合し、ReviewSession形式で出力

必ずstructure_review_resultsツールを使用して最終結果を作成してください。
""",
        sub_agents=sub_agents,
        tools=[structure_tool],
    )

    return agent


# Export the agent for ADK Web auto-discovery
root_agent = create_review_orchestrator_agent(model="gemini-2.5-flash")
