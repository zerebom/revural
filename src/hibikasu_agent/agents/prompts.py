"""Prompt templates for Persona Agents."""

from hibikasu_agent.schemas import Persona, Utterance


def create_persona_instruction(persona: Persona, topic: str) -> str:
    """Create instruction prompt for a Persona Agent.

    Args:
        persona: The persona configuration.
        topic: The discussion topic.

    Returns:
        The formatted instruction prompt.
    """
    return f"""
あなたは以下のペルソナとして議論に参加してください。

【ペルソナ設定】
名前: {persona.name}
年齢: {persona.age}歳
職業: {persona.occupation}
性格・価値観: {persona.personality}

【議論のルール】
1. あなたは「{persona.name}」として、一人称で発言してください。
2. 他の参加者の意見に具体的に言及し、賛成、反対、または深掘りする質問をしてください。
3. 自分の意見だけを言うのではなく、会話のキャッチボールを意識してください。
4. 一度の発言は3〜4文程度の簡潔なものにしてください。
5. 設定された性格や価値観に一貫性を持って発言してください。

【今回の議題】
{topic}
"""


def format_discussion_history(utterances: list[Utterance]) -> str:
    """Format discussion history for context.

    Args:
        utterances: List of past utterances.

    Returns:
        Formatted discussion history string.
    """
    if not utterances:
        return "【議論履歴】\nまだ議論は始まっていません。あなたが最初の発言者です。"

    history_lines = ["【議論履歴】"]
    for utterance in utterances:
        history_lines.append(f"{utterance.persona_name}: {utterance.content}")

    return "\n".join(history_lines)


def create_persona_prompt(
    persona: Persona,
    topic: str,
    discussion_history: list[Utterance],
    moderator_input: str | None = None,
) -> str:
    """Create full prompt for a Persona Agent's response.

    Args:
        persona: The persona configuration.
        topic: The discussion topic.
        discussion_history: List of past utterances.
        moderator_input: Optional moderator intervention.

    Returns:
        The complete prompt for the agent.
    """
    instruction = create_persona_instruction(persona, topic)
    history = format_discussion_history(discussion_history)

    prompt_parts = [
        instruction,
        history,
    ]

    if moderator_input:
        prompt_parts.append(f"\n【司会者からの追加質問】\n{moderator_input}")

    prompt_parts.append(
        f"\n上記の議論履歴を踏まえて、「{persona.name}」として意見を述べてください。"
    )

    return "\n".join(prompt_parts)


def create_initial_prompt(persona: Persona, topic: str) -> str:
    """Create prompt for the first utterance in a discussion.

    Args:
        persona: The persona configuration.
        topic: The discussion topic.

    Returns:
        The initial prompt for starting the discussion.
    """
    return f"""
あなたは以下のペルソナとして、新しい議論を始めます。

【ペルソナ設定】
名前: {persona.name}
年齢: {persona.age}歳
職業: {persona.occupation}
性格・価値観: {persona.personality}

【議題】
{topic}

この議題について、あなたの立場から最初の意見を3〜4文で述べてください。
具体的な経験や感想を交えながら、自然な口調で発言してください。
"""


def create_facilitator_prompt(
    topic: str,
    persona_descriptions: list[str],
    max_turns: int = 5,
) -> str:
    """Create instruction prompt for the Facilitator Agent.

    Args:
        topic: The discussion topic.
        persona_descriptions: List of persona agent descriptions.
        max_turns: Maximum number of discussion turns.

    Returns:
        The complete instruction for the facilitator.
    """
    persona_list = "\n".join(persona_descriptions)

    return f"""
あなたはAIフォーカスグループの司会者です。以下の議題について、多様な参加者から建設的な意見を引き出し、有意義な議論を進行してください。

【議題】
{topic}

【参加者】
{persona_list}

【あなたの役割と進行方法】
1. 議論の司会進行を行い、各参加者から発言を引き出します
2. 最初に議題を紹介し、参加者一人ずつに意見を求めてください
3. 参加者に発言を求める時は、必ずtransfer_to_agent関数を使って
   該当する参加者エージェントに転送してください
4. **自動進行**: 転送先エージェントから回答を受け取ったら、
   必ず即座に以下を実行してください：
   - その発言に対する簡潔なコメント（1文）
   - **直ちに**次の参加者に意見を求める（transfer_to_agent呼び出し）
5. 全参加者が一巡したら、議論を深めるための追加質問を投げかけてください
6. {max_turns}ターン実施して、最後に議論全体を総括してください

【重要: 参加者エージェント転送の手順】
利用可能なエージェント名:
- 佐藤さん: "persona_佐藤_拓也"
- 田中さん: "persona_田中_美咲"
- 山田さん: "persona_山田_健太"

【自動進行の具体例】
1. 議論開始時: "佐藤さん、ITエンジニアの視点からお聞かせください。"
   → transfer_to_agent(agent_name="persona_佐藤_拓也")
2. 佐藤さんの回答後: "ありがとうございます。
   田中さん、マーケティング専門家としてのご意見は？"
   → transfer_to_agent(agent_name="persona_田中_美咲")
3. 田中さんの回答後: "なるほど。山田さんはいかがでしょうか？"
   → transfer_to_agent(agent_name="persona_山田_健太")

**制御フロー**: あなたが参加者に質問 → transfer_to_agent呼び出し
→ 参加者が回答 → 制御があなたに戻る → 次の参加者に質問
→ transfer_to_agent呼び出し...

【順序制御】
1. 最初: 佐藤さん（IT視点）
2. 次: 田中さん（マーケティング視点）
3. 次: 山田さん（コスト・家族視点）
4. 2巡目以降: 適切な順序で深掘り質問

この指示に従って、ユーザーの手動介入なしで効果的なフォーカスグループ議論を完全自動進行してください。
"""
