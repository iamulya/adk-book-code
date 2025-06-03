
# tools_examples/crewai_adapter_agent.py
from google.adk.agents import Agent
from google.adk.tools.crewai_tool import CrewaiTool 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()
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
            name="crewai_search_user", model=DEFAULT_LLM,
            instruction="You can search Google using the SerperDevTool.",
            tools=[adk_wrapped_serper]
        )
        print("CrewaiTool wrapper initialized.")
    else: print("SERPER_API_KEY not set. Skipping CrewAI SerperDevTool example.")
except ImportError:
    print("CrewAI or SerperDevTool not found.")
if __name__ == "__main__":
    if crewai_integrated_agent:
        print("CrewAI Agent ready. Run with SERPER_API_KEY set to test.")
        runner = InMemoryRunner(agent=crewai_integrated_agent, app_name="CrewAIApp")
        session_id = "s_crewai_test"
        user_id = "crewai_user"
        create_session(runner, session_id, user_id)

        prompt = "What is CrewAI?"
        print(f"\nYOU: {prompt}")
        user_message = Content(parts=[Part(text=prompt)], role="user")
        print("ASSISTANT: ", end="", flush=True)
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text:
                print(event.content.parts[0].text, end="")
        print()
