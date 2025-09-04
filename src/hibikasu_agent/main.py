"""Main entry point for ADK Web integration (Parallel Orchestrator)."""

from hibikasu_agent.agents.parallel_orchestrator import create_parallel_review_agent

# Use the parallel orchestrator pipeline as root
root_agent = create_parallel_review_agent(model="gemini-2.5-flash")
