"""UX Designer Specialist Agent for ADK Web discovery."""

from hibikasu_agent.agents.specialist import create_ux_designer_agent

# Export the agent for ADK Web auto-discovery
root_agent = create_ux_designer_agent(model="gemini-2.5-flash")
