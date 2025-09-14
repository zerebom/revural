"""Parallel Orchestrator that aggregates specialist issues into FinalIssue list.

This agent orchestrates four specialist agents via AgentTool with summarization
disabled, then aggregates their typed outputs into FinalIssuesResponse.
"""

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import AgentTool

from hibikasu_agent.agents.specialist import (
    create_role_agents,
    create_specialist_from_role,
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
            "`engineer_specialist`, `ux_designer_specialist`, "
            "`qa_tester_specialist`, `pm_specialist`."
        ),
        tools=[engineer_tool, ux_tool, qa_tool, pm_tool],
    )

    # 4) Step 2 Agent: Aggregates the results from state.
    # aggregate_tool = FunctionTool(aggregate_final_issues)
    merger = LlmAgent(
        name="IssueAggregatorMerger",
        model=model,
        description=("Aggregates parallel specialist outputs into a prioritized final list."),
        instruction=(
            "# あなたの役割\n"
            "あなたは、4つの専門家チーム（エンジニア、UXデザイナー、QAテスター、プロダクトマネージャー）からの"
            "PRDレビュー結果を集約し、経営陣への報告に向けて最終的な指摘事項リストを作成する、"
            "経験豊富なシニアプロダクトマネージャーです。あなたの仕事は、単なる情報の結合ではなく、"
            "高度な分析と判断を通じて、本質的で実行可能なアクションアイテムへと昇華させることです。\n\n"
            "# 入力情報\n"
            "あなたは、以下の4つのJSONオブジェクトをコンテキストとして受け取ります。これらは各専門家チームからの報告書です。\n"
            "- エンジニアチームの指摘: {engineer_issues}\n"
            "- UXデザイナーチームの指摘: {ux_designer_issues}\n"
            "- QAテスターチームの指摘: {qa_tester_issues}\n"
            "- プロダクトマネージャーチームの指摘: {pm_issues}\n\n"
            "# あなたが実行すべきタスク\n"
            "以下の思考プロセスに従い、最終的な指摘事項リストを生成してください。\n\n"
            "**Step 1: 全指摘事項の把握**\n"
            "まず、4つのチームから提出されたすべての指摘事項（issues）に注意深く目を通し、全体像を完全に理解してください。\n\n"
            "**Step 2: 重複・関連指摘の特定とグループ化**\n"
            "次に、異なるチームから提出されているが、根本的な原因や対象が同じである指摘事項を特定します。\n"
            "- 例1：「パスワードリセット機能がない」という指摘がUXデザイナーとQAテスターの両方から挙がっている。\n"
            "- 例2：「セキュアなセッション管理」に関する指摘がエンジニアとQAテスターから挙がっている。\n"
            "これらの重複または強く関連する指摘を、心の中でグループ化してください。\n\n"
            "**Step 3: 指摘の統合と洗練**\n"
            "グループ化した指摘を、最も的確で包括的な一つの指摘に統合します。\n"
            "- **コメントの統合**: 各チームの視点を組み合わせ、より質の高いコメントに書き換えます。"
            "なぜそれが問題なのか、どのような影響があるのかを明確にしてください。\n"
            "- **担当エージェントの決定**: 統合後の指摘は、その内容を最も代表する専門家チームの名前を"
            "`agent_name`として設定してください。判断に迷う場合は、より影響範囲の広い視点"
            "（例：技術的な問題よりもプロダクト戦略の問題ならPM）を優先してください。\n"
            "- **重要度の再評価**: `severity`は、統合された視点から再評価してください。\n\n"
            "**Step 4: 全体最適化のための優先順位付け**\n"
            "統合・洗練されたすべての指摘事項をリストアップし、ビジネス全体へのインパクト、"
            "ユーザー体験への影響、開発の緊急性、実現可能性を総合的に考慮して、"
            "1から始まる通しの優先順位（`priority`）を付け直してください。"
            "これがあなたの最も重要な仕事です。数値が小さいほど優先度が高くなります。\n\n"
            "**Step 5: 最終出力の生成**\n"
            "最後に、上記のプロセスを経て完成した指摘事項のリストを、以下のスキーマに厳密に従った単一のJSONオブジェクトとして出力してください。\n\n"
            "# 出力に関する厳格なルール\n"
            "- あなたの応答は、JSONオブジェクト**のみ**でなければなりません。\n"
            "- 説明文、前置き、後書き、マークダウンのコードフェンス（```json）など、"
            "JSON以外のテキストを一切含めないでください。\n"
            '- 出力は必ず `{{"final_review_issues": [...]}}` というキー構造を持つ必要があります。\n\n'
            "思考プロセスを丁寧に行い、最高品質の最終報告書を作成してください。"
        ),
        # tools=[aggregate_tool],
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
