
# hello_adk_agent/agent.py
from google.adk.agents import Agent
root_agent = Agent(
    name="greeting_agent", model="gemini-2.0-flash",
    instruction="You are a cheerful agent that greets the user and asks how you can help them.",
    description="A friendly agent that initiates conversations.",
)

