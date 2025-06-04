from .agent import root_agent # Imports root_agent from agent.py
from vertexai.preview.reasoning_engines import AdkApp

# enable_tracing can be True or False depending on your needs
adk_app = AdkApp(
  agent=root_agent,
  enable_tracing=True,
)