import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import Agent 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from ..utils import load_environment_variables

load_environment_variables()

root_agent = Agent(
    name="simple_assistant",
    model="gemini-2.0-flash",
    instruction="You are a friendly and helpful assistant. Be concise.",
    description="A basic assistant to answer questions.",
)

if __name__ == "__main__":
    print("Initializing Simple Assistant...")
    runner = InMemoryRunner(agent=root_agent, app_name="MySimpleApp")

    current_session_id = "my_first_session"
    current_user_id = "local_dev_user"

    # --- Create the session before the loop ---
    print(f"Creating session: {current_session_id} for user: {current_user_id} on app: {runner.app_name}")
    # Since session_service.create_session is async, we need to run it in an event loop
    try:
        asyncio.run(runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=current_user_id,
            session_id=current_session_id,
        ))
        print("Session created successfully.")
    except Exception as e:
        print(f"Error creating session: {e}")
        exit()
    # --- Session creation done ---

    print("Simple Assistant is ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Exiting Simple Assistant. Goodbye!")
            break
        if not user_input.strip():
            continue

        user_message = Content(parts=[Part(text=user_input)], role="user")
        print("Assistant: ", end="", flush=True)
        try:
            for event in runner.run(
                user_id=current_user_id,
                session_id=current_session_id,
                new_message=user_message,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
            print()
        except Exception as e:
            print(f"\nAn error occurred: {e}")