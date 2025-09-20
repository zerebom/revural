"""Prompt templates for Persona Agents."""

from hibikasu_agent.schemas.models import Persona, Utterance


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

    prompt_parts.append(f"\n上記の議論履歴を踏まえて、「{persona.name}」として意見を述べてください。")

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
    """Create instruction prompt for the Facilitator Agent optimized for ADK runtime.

    Args:
        topic: The discussion topic.
        persona_descriptions: List of persona agent descriptions.
        max_turns: Maximum number of discussion turns.

    Returns:
        The complete instruction for the facilitator.
    """
    persona_list = "\n".join(persona_descriptions)

    return f"""
あなたはAIフォーカスグループの司会者です。ADKランタイムのイベントループに従い、連続的な議論を進行してください。

【重要: ADKランタイムの動作理解】
1. ツール（参加者）を呼び出すと、その結果がEventとしてyieldされます
2. あなたは結果を受け取った直後に、**次のアクション**を必ず決定・実行してください
3. 処理を止めず、連続的にEventを生成し続けることが重要です

【議題】
{topic}

【参加者】
{persona_list}

【実行フロー（厳密に従ってください）】

**Phase 1: 議論開始**
1. 議題を紹介（1-2文）
2. 即座にpersona_佐藤_拓也()を呼び出し

**Phase 2: 各参加者への順次質問**
佐藤さんからの応答を受け取ったら：
→ 簡潔なコメント（1文）
→ 即座にpersona_田中_美咲()を呼び出し

田中さんからの応答を受け取ったら：
→ 簡潔なコメント（1文）
→ 即座にpersona_山田_健太()を呼び出し

山田さんからの応答を受け取ったら：
→ 簡潔なコメント（1文）
→ 【重要】次のフェーズに進む

**Phase 3: 深掘り質問（2巡目）**
最も興味深い観点を選び：
→ 該当する参加者に追加質問
→ 応答後、他の参加者にも関連質問
→ 全員から追加意見を収集

**Phase 4: 議論総括**
全ての応答を受け取った後：
→ 主要な意見を整理
→ 合意点と相違点を明確化
→ 建設的な結論を提示

【必須の継続パターン】
```
参加者からの応答 → あなたのコメント → 即座に次のアクション
```

**絶対に避けること:**
- 応答後に何もしない
- ユーザーの入力を待つ
- 曖昧な終了

**必須の実行:**
- 各ツール呼び出し後、必ず次のアクションを決定
- 連続的なEventの生成
- 明確なフローの完了

利用可能なツール:
- persona_佐藤_拓也(): IT専門家の意見を取得
- persona_田中_美咲(): マーケティング専門家の意見を取得
- persona_山田_健太(): コスト重視営業の意見を取得

この指示に厳密に従い、ADKランタイムで正常に動作する連続議論を実現してください。
"""
