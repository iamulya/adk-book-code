
# tools_examples/langchain_adapter_agent.py
from google.adk.agents import Agent
from google.adk.tools import LangchainTool 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
langchain_integrated_agent = None
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    langchain_search_tool_instance = DuckDuckGoSearchRun()
    adk_wrapped_duckduckgo = LangchainTool(
        tool=langchain_search_tool_instance, name="internet_search_duckduckgo", 
        description="A wrapper for DuckDuckGo Search."
    )
    langchain_integrated_agent = Agent(
        name="langchain_search_user", model="gemini-1.5-flash-latest",
        instruction="You can search the internet using DuckDuckGo.",
        tools=[adk_wrapped_duckduckgo]
    )
    print("LangchainTool wrapper initialized.")
except ImportError:
    print("Langchain or DuckDuckGoSearchRun not found.")
if __name__ == "__main__":
    if langchain_integrated_agent:
        runner = InMemoryRunner(agent=langchain_integrated_agent, app_name="LangchainApp")
        prompt = "What is Langchain?"
        print(f"\nYOU: {prompt}")
        user_message = Content(parts=[Part(text=prompt)])
        print("ASSISTANT: ", end="", flush=True)
        for event in runner.run(user_id="lc_user", session_id="s_lc", new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text:
                print(event.content.parts[0].text, end="")
        print()

