"""Review Orchestrator Agent for ADK Web discovery."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, agent_tool

from hibikasu_agent.agents.orchestrator.tools import structure_review_results
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
ユーザーからPRDを受け取ったら、以下の手順で必ずレビューを実行してください：

【重要な処理フロー】
1. ユーザーからPRDテキストを受け取る
2. 以下の全ての専門エージェントツールを呼び出してレビューを実行：
   - engineer_specialist: バックエンドエンジニアの視点でPRDをレビュー
   - ux_designer_specialist: UXデザイナーの視点でPRDをレビュー
   - qa_tester_specialist: QAテスターの視点でPRDをレビュー
   - pm_specialist: プロダクトマネージャーの視点でPRDをレビュー
3. **必ず structure_review_results ツールを使用して、
   全てのレビュー結果を構造化データにまとめる**
4. **structure_review_results ツールの出力をそのまま最終回答として返す**

【超重要】
- 全ての専門エージェントツールを呼び出した後、
  必ず structure_review_results ツールを使用すること
- structure_review_results ツールには、
  PRDテキストと各エージェントのレビュー結果を渡すこと
- structure_review_results ツールの出力があなたの最終的な返答となる
- Markdown形式での要約は不要。構造化されたデータのみを返すこと
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

    # Add the structure_review_results tool
    structure_tool = FunctionTool(structure_review_results)

    # Combine all tools
    all_tools = [*specialist_tools, structure_tool]

    agent = LlmAgent(
        name="review_orchestrator",
        model=model,
        description="PRDレビューを統合管理するオーケストレーター",
        instruction=instruction.strip(),
        tools=all_tools,  # type: ignore[arg-type]
    )

    return agent


# Export the agent for ADK Web auto-discovery
root_agent = create_review_orchestrator_agent(model="gemini-2.5-flash")
