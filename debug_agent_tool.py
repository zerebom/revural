#!/usr/bin/env python
"""Debug AgentTool behavior with output_schema."""

import asyncio
from uuid import uuid4

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types

from src.hibikasu_agent.agents.specialist import create_specialist_from_role

# Load environment variables
load_dotenv()


async def test_agent_tool_output():
    """Test what AgentTool returns when agent has output_schema."""

    # Create engineer agent with output_schema
    agent = create_specialist_from_role(
        "engineer",
        name="engineer_specialist",
        description="バックエンドエンジニアの専門的観点からPRDをレビュー",
    )

    # Create runner
    app_name = "debug_test"
    runner = InMemoryRunner(agent=agent, app_name=app_name)

    # Create session
    session_id = str(uuid4())
    user_id = "test_user"
    await runner.session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

    # Test message
    test_prd = "テスト用PRD: ユーザー登録機能を作る"
    message = types.Content(parts=[types.Part(text=test_prd)], role="user")

    # Run agent and collect response
    result = None
    async for event in runner.run_async(
        session_id=session_id,
        user_id=user_id,
        new_message=message,
    ):
        if hasattr(event, "content") and event.content is not None:
            content = event.content
            if hasattr(content, "parts") and content.parts:
                first_part = content.parts[0]
                if hasattr(first_part, "text"):
                    result = first_part.text
                    print(f"Agent returned text: {type(result)}")
                    print(f"Content: {result}")
                elif hasattr(first_part, "function_response"):
                    result = first_part.function_response.response
                    print(f"Agent returned function_response: {type(result)}")
                    print(f"Content: {result}")

    return result


if __name__ == "__main__":
    asyncio.run(test_agent_tool_output())
