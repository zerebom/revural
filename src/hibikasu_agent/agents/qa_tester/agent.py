"""QA Tester Specialist Agent for ADK Web discovery."""

from hibikasu_agent.agents.specialist import create_specialist_from_role

# Export the agent for ADK Web auto-discovery
root_agent = create_specialist_from_role(
    "qa_tester",
    name="qa_tester_specialist",
    description="QAテスターの専門的観点からPRDをレビュー",
    model="gemini-2.5-flash",
)
