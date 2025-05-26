
# tools_examples/crewai_adapter_agent.py
from google.adk.agents import Agent
from google.adk.tools import CrewaiTool 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os
crewai_integrated_agent = None
try:
    from crewai_tools import SerperDevTool 
    if os.getenv("SERPER_API_KEY"):
        crewai_serper_tool_instance = SerperDevTool()
        adk_wrapped_serper = CrewaiTool(
            tool=crewai_serper_tool_instance, name="google_search_serper", 
            description=crewai_serper_tool_instance.description or "A tool to search Google using Serper API."
        )
        crewai_integrated_agent = Agent(
            name="crewai_search_user", model="gemini-2.0-flash",
            instruction="You can search Google using the SerperDevTool.",
            tools=[adk_wrapped_serper]
        )
        print("CrewaiTool wrapper initialized.")
    else: print("SERPER_API_KEY not set. Skipping CrewAI SerperDevTool example.")
except ImportError:
    print("CrewAI or SerperDevTool not found.")
if __name__ == "__main__":
    if crewai_integrated_agent:
        # ... (runner logic as in book) ...
        print("CrewAI Agent ready. Run with SERPER_API_KEY set to test.")

