"""Engineer Specialist Agent for ADK Web discovery."""

from hibikasu_agent.agents.specialist import create_engineer_agent

# Export the agent for ADK Web auto-discovery
root_agent = create_engineer_agent(model="gemini-2.5-flash")
