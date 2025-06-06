from google.adk.agents import Agent
from google.adk.tools import google_search # Import the pre-built tool
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from building_intelligent_agents.utils import create_session, load_environment_variables, DEFAULT_LLM

load_environment_variables()

search_savvy_agent = Agent(
    name="search_savvy_agent",
    model=DEFAULT_LLM, 
    instruction="You are a helpful research assistant. Use Google Search when you need to find current information or verify facts.",
    tools=[google_search] # Add the tool instance
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=search_savvy_agent, app_name="SearchApp")
    prompts = [
        "What is the latest news about the Mars rover Perseverance?",
        "Who won the latest Formula 1 race?",
        "What is the capital of France?" 
    ]

    session_id = "search_session"
    user_id = "search_user"

    create_session(runner, session_id, user_id)

    for prompt_text in prompts:
        print(f"\nYOU: {prompt_text}")
        user_message = Content(parts=[Part(text=prompt_text)], role="user")

        print("ASSISTANT: ", end="", flush=True)
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
                    # With search, grounding metadata might be present
                    if event.grounding_metadata and event.grounding_metadata.web_search_queries:
                        print(f"\n  (Searched for: {event.grounding_metadata.web_search_queries})", end="")
        print()