"""QA Tester Specialist Agent for ADK Web discovery."""

from hibikasu_agent.agents.specialist import create_qa_tester_agent

# Export the agent for ADK Web auto-discovery
root_agent = create_qa_tester_agent(model="gemini-2.5-flash")
