
# multi_agent_systems/hierarchical_structure.py
from google.adk.agents import Agent 
research_sub_agent = Agent(
    name="researcher", model="gemini-1.5-flash-latest",
    instruction="You are a research specialist. Find relevant information using search tools.",
    description="Finds information on a given topic.",
)
writer_sub_agent = Agent(
    name="writer", model="gemini-1.5-flash-latest",
    instruction="You are a skilled writer. Synthesize information into a coherent summary.",
    description="Writes summaries or reports based on provided information."
)
report_orchestrator_agent = Agent(
    name="report_orchestrator", model="gemini-1.5-pro-latest", 
    instruction="Orchestrate report creation. Use 'researcher', then 'writer'. Present final report.",
    description="Orchestrates research and writing of reports.",
    sub_agents=[research_sub_agent, writer_sub_agent]
)

