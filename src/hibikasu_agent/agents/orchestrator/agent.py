"""Review Orchestrator Agent for ADK Web discovery."""

from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool

from hibikasu_agent.agents.specialist import (
    create_engineer_agent,
    create_pm_agent,
    create_qa_tester_agent,
    create_ux_designer_agent,
)


def create_review_orchestrator_agent(model: str = "gemini-2.5-flash") -> LlmAgent:
    """Create Review Orchestrator Agent using AgentTool pattern."""

    instruction = """
あなたはPRDレビューオーケストレーターです。
ユーザーからPRDを受け取ったら、以下のツールを使って各専門エージェントにレビューを依頼してください：

- engineer_specialist: バックエンドエンジニアの視点でPRDをレビュー
- ux_designer_specialist: UXデザイナーの視点でPRDをレビュー
- qa_tester_specialist: QAテスターの視点でPRDをレビュー
- pm_specialist: プロダクトマネージャーの視点でPRDをレビュー

【処理フロー】
1. ユーザーからPRDテキストを受け取る
2. 各専門エージェントツールを呼び出してレビューを実行
3. 全ての結果を統合・優先順位付け
4. 最終的な論点リストを以下の形式で提示

【レビュー結果の形式】
## 重要度：高
- [具体的な指摘内容（担当エージェント名も記載）]

## 重要度：中
- [具体的な指摘内容（担当エージェント名も記載）]

## 重要度：低
- [具体的な指摘内容（担当エージェント名も記載）]

PRDを受け取ったら、必ず全ての専門エージェントツールを呼び出してレビューを実行してください。
"""

    # Import specialist agents

    # Create specialist agents and wrap them in AgentTools
    engineer_agent = create_engineer_agent(model=model)
    ux_designer_agent = create_ux_designer_agent(model=model)
    qa_tester_agent = create_qa_tester_agent(model=model)
    pm_agent = create_pm_agent(model=model)

    specialist_tools = [
        agent_tool.AgentTool(agent=engineer_agent),
        agent_tool.AgentTool(agent=ux_designer_agent),
        agent_tool.AgentTool(agent=qa_tester_agent),
        agent_tool.AgentTool(agent=pm_agent),
    ]

    agent = LlmAgent(
        name="review_orchestrator",
        model=model,
        description="PRDレビューを統合管理するオーケストレーター",
        instruction=instruction.strip(),
        tools=specialist_tools,  # type: ignore[arg-type]
    )

    return agent


# Export the agent for ADK Web auto-discovery
root_agent = create_review_orchestrator_agent(model="gemini-2.5-flash")
