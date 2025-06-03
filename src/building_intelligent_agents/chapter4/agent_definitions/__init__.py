# Import the root_agent from your app module
from .callback_agent import root_agent

# Create a simple object or module-like structure named 'agent'
# and assign root_agent to it. This mimics the structure ADK might expect.
class AgentModulePlaceholder:
    pass

agent = AgentModulePlaceholder()
agent.root_agent = root_agent # type: ignore