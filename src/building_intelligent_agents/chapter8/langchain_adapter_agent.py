
# tools_examples/langchain_adapter_agent.py
from google.adk.agents import Agent
from google.adk.tools.langchain_tool import LangchainTool 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

langchain_integrated_agent = None
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    langchain_search_tool_instance = DuckDuckGoSearchRun()
    adk_wrapped_duckduckgo = LangchainTool(
        tool=langchain_search_tool_instance, name="internet_search_duckduckgo", 
        description="A wrapper for DuckDuckGo Search."
    )
    langchain_integrated_agent = Agent(
        name="langchain_search_user", model=DEFAULT_LLM,
        instruction="You can search the internet using DuckDuckGo.",
        tools=[adk_wrapped_duckduckgo]
    )
    print("LangchainTool wrapper initialized.")
except ImportError:
    print("Langchain or DuckDuckGoSearchRun not found.")
if __name__ == "__main__":
    if langchain_integrated_agent:
        runner = InMemoryRunner(agent=langchain_integrated_agent, app_name="LangchainApp")
        session_id = "s_langchain_test"
        user_id = "langchain_user"
        create_session(runner, session_id, user_id)
        prompt = "What is Langchain?"
        print(f"\nYOU: {prompt}")
        user_message = Content(parts=[Part(text=prompt)], role="user")
        print("ASSISTANT: ", end="", flush=True)
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text:
                print(event.content.parts[0].text, end="")
        print()

