"""Main entry point for ADK Web integration."""

from hibikasu_agent.agents.orchestrator import create_review_orchestrator_agent

# Create the review orchestrator agent for ADK Web
root_agent = create_review_orchestrator_agent(model="gemini-2.5-flash")
