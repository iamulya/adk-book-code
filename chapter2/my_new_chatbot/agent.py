
# my_new_chatbot/agent.py
from google.adk.agents import Agent
root_agent = Agent(
    name="ui_test_agent", model="gemini-1.5-flash-latest",
    instruction="You are a helpful assistant designed for the ADK Dev UI.",
)

