
# my_new_chatbot/agent.py
from google.adk.agents import Agent
root_agent = Agent(
    name="ui_test_agent", model="gemini-2.0-flash",
    instruction="You are a helpful assistant designed for the ADK Dev UI.",
)

