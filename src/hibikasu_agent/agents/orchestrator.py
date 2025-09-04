"""Review Orchestrator Agent implementation using Workflow Triage pattern."""

from google.adk.agents import LlmAgent

from hibikasu_agent.agents.specialist import create_specialist_from_role
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


def create_review_orchestrator_agent(model: str = "gemini-2.5-flash") -> LlmAgent:
    """Create Review Orchestrator Agent using Workflow Triage pattern.

    Args:
        model: LLM model to use

    Returns:
        LlmAgent configured as review orchestrator with specialist sub_agents
    """
    logger.info("Creating Review Orchestrator Agent with specialist sub_agents")

    # Create specialist agents
    engineer_agent = create_specialist_from_role(
        "engineer",
        name="engineer_specialist",
        description="バックエンドエンジニアの専門的観点からPRDをレビュー",
        model=model,
    )
    ux_designer_agent = create_specialist_from_role(
        "ux_designer",
        name="ux_designer_specialist",
        description="UXデザイナーの専門的観点からPRDをレビュー",
        model=model,
    )
    qa_tester_agent = create_specialist_from_role(
        "qa_tester",
        name="qa_tester_specialist",
        description="QAテスターの専門的観点からPRDをレビュー",
        model=model,
    )
    pm_agent = create_specialist_from_role(
        "pm",
        name="pm_specialist",
        description="プロダクトマネージャーの専門的観点からPRDをレビュー",
        model=model,
    )

    instruction = """
あなたはPRDレビューオーケストレーターです。
複数の専門エージェント（エンジニア、UXデザイナー、QAテスター、プロダクトマネージャー）を活用して、
効果的なPRDレビューを実行してください。

【役割】
1. ユーザーからPRDを受け取り、専門エージェント群に並行レビューを依頼
2. 各専門エージェントからの指摘を統合・優先順位付け
3. ユーザーとの対話で論点を深掘り
4. 修正案の提案と適用

【処理フロー】
1. PRDレビュー依頼→specialist agentsに並行実行指示
2. 各agentからの指摘を収集・統合
3. 優先順位付けして最終論点リスト生成
4. ユーザーとの対話で論点深掘り・修正案提案

【利用可能な専門エージェント】
- engineer_specialist: バックエンドエンジニアの観点
- ux_designer_specialist: UXデザイナーの観点
- qa_tester_specialist: QAテスターの観点
- pm_specialist: プロダクトマネージャーの観点

ユーザーのPRDレビュー依頼に対して、適切な専門エージェントに並行して作業を依頼し、
結果を統合して包括的なレビューを提供してください。

特定の論点について詳細な質問があった場合は、該当する専門エージェントに詳細を確認してください。
"""

    agent = LlmAgent(
        name="review_orchestrator",
        model=model,
        description="PRDレビューを統合管理するオーケストレーター",
        instruction=instruction.strip(),
        sub_agents=[
            engineer_agent,
            ux_designer_agent,
            qa_tester_agent,
            pm_agent,
        ],
    )

    logger.info(
        "Review Orchestrator Agent created with 4 specialist sub_agents", model=model
    )

    return agent
