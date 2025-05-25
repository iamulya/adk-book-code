
# flows_planners_examples/basic_flow_agent.py
from google.adk.agents import Agent
simple_tool_user_agent = Agent(
    name="simple_tool_user", model="gemini-1.5-flash-latest",
    instruction="Use tools if needed to answer questions.",
)
# orchestrator_agent = Agent(
#     name="orchestrator", model="gemini-1.5-pro-latest",
#     instruction="Coordinate tasks. You can delegate to sub_agents.",
#     sub_agents=[simple_tool_user_agent]
# )

