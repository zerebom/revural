"""Main entry point for ADK Web integration (Parallel Orchestrator)."""

from hibikasu_agent.agents.parallel_orchestrator import load_review_pipeline

root_agent = load_review_pipeline()
