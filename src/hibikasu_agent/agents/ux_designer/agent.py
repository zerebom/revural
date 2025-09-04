"""UX Designer Specialist Agent for ADK Web discovery."""

from hibikasu_agent.agents.specialist import create_specialist_from_role

# Export the agent for ADK Web auto-discovery
root_agent = create_specialist_from_role(
    "ux_designer",
    name="ux_designer_specialist",
    description="UXデザイナーの専門的観点からPRDをレビュー",
    model="gemini-2.5-flash",
)
