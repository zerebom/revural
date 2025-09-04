"""Engineer Specialist Agent for ADK Web discovery."""

from hibikasu_agent.agents.specialist import create_specialist_from_role

# Export the agent for ADK Web auto-discovery
root_agent = create_specialist_from_role(
    "engineer",
    name="engineer_specialist",
    description="バックエンドエンジニアの専門的観点からPRDをレビュー",
    model="gemini-2.5-flash",
)
