# runner_examples/runner_invocation.py
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner # InMemoryRunner is a pre-configured Runner
from google.genai.types import Content, Part

from ...utils import load_environment_variables, create_session
load_environment_variables()  # Load environment variables for ADK configuration

greet_agent = Agent(name="greeter", model="gemini-2.0-flash", instruction="Greet the user warmly.")
runner = InMemoryRunner(agent=greet_agent, app_name="GreetApp")

user_msg = Content(parts=[Part(text="Hello there!")], role="user")  # User message to the agent

async def use_run_async():
    print("\\n--- Using run_async ---")
    session_id = "s_async"  
    user_id = "async_user"
    create_session(runner, user_id=user_id, session_id=session_id)
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_msg):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"Async Event from {event.author}: {event.content.parts[0].text.strip()}")

def use_run_sync():
    print("\\n--- Using run (sync wrapper) ---")
    session_id = "s_sync"  
    user_id = "sync_user"
    create_session(runner, user_id=user_id, session_id=session_id)
    for event in runner.run(user_id="sync_user", session_id="s_sync", new_message=user_msg):
        if event.content and event.content.parts and event.content.parts[0].text:
             print(f"Sync Event from {event.author}: {event.content.parts[0].text.strip()}")
