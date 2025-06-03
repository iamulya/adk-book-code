
# my_new_chatbot/agent.py
from google.adk.agents import Agent
from building_intelligent_agents.utils import DEFAULT_LLM, load_environment_variables   
load_environment_variables()

root_agent = Agent(
    name="ui_test_agent", model=DEFAULT_LLM,
    instruction="You are a helpful assistant designed for the ADK Dev UI.",
)

