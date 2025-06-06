from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.load_web_page import load_web_page # The function itself
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

# Ensure you have the necessary libraries: pip install requests beautifulsoup4 lxml
# Create the FunctionTool
web_page_loader_tool = FunctionTool(func=load_web_page)
# You can customize name and description if needed:
# web_page_loader_tool.name = "fetch_web_content"
# web_page_loader_tool.description = "Fetches and extracts text content from a given URL."

browser_agent = Agent(
    name="web_browser_agent",
    model=DEFAULT_LLM,
    instruction="You are an assistant that can fetch content from web pages using the provided tool and then answer questions about it or summarize it.",
    tools=[web_page_loader_tool]
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=browser_agent, app_name="BrowserApp")

    session_id = "browse_session"
    user_id = "browse_user"

    create_session(runner, session_id, user_id)

    prompts = [
        "Can you get the main text from [https://www.python.org/] and summarize it in one sentence?"
    ]

    for prompt_text in prompts:
        print(f"\nYOU: {prompt_text}")
        user_message = Content(parts=[Part(text=prompt_text)], role="user")
        print("ASSISTANT: ", end="", flush=True)

        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        print()
