"""Product manager specialist agent for ADK auto-discovery."""

from hibikasu_agent.agents.specialist import create_specialist_for_role

# Export the agent for ADK Web auto-discovery
root_agent = create_specialist_for_role("pm")
