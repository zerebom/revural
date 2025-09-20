"""Coordinator agent utilities for the parallel orchestrator."""

from google.adk.agents import LlmAgent

from hibikasu_agent.agents.specialist import create_role_agents


def create_coordinator_agent(model: str = "gemini-2.5-flash-lite") -> LlmAgent:
    """Coordinator that routes by free-text to specialist chat agents."""

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

    return LlmAgent(
        name="Coordinator",
        model=model,
        description="Routes incoming issue text to the best specialist chat agent.",
        instruction=(
            "あなたは司令塔エージェントです。ユーザーの課題/質問のテキストを読み、\n"
            "最も適切な専門家（engineer_chat / ux_designer_chat / qa_tester_chat / pm_chat）へ\n"
            "transfer_to_agent(agent_name=...) を用いて会話を移譲してください。\n"
            "- 技術設計・実装・パフォーマンス・セキュリティ → engineer_chat\n"
            "- UX・UI・ユーザーフロー・情報設計 → ux_designer_chat\n"
            "- テスト観点・品質リスク・再現手順 → qa_tester_chat\n"
            "- 企画・優先度・ステークホルダー調整・KPI → pm_chat\n"
            "曖昧な場合は短く確認の質問をしてから転送先を決定してください。\n"
        ),
        sub_agents=[eng_chat, ux_chat, qa_chat, pm_chat],
    )
