
# agent_definitions/creative_writer.py
import asyncio
import os
from google.adk.agents import Agent
from google.genai.types import GenerateContentConfig, SafetySetting, HarmCategory, HarmBlockThreshold
from ...utils import load_environment_variables

load_environment_variables()

custom_safety_settings = [
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_NONE),
]

creative_writer_agent = Agent(
    name="creative_writer", model="gemini-2.0-flash", 
    instruction="You are a creative writer. Write a short, imaginative story based on the user's prompt.",
    description="Generates short creative stories.",
    generate_content_config=GenerateContentConfig(
        temperature=0.9, top_p=0.95, top_k=40, max_output_tokens=1024,
        safety_settings=custom_safety_settings)
)
if __name__ == "__main__":
    from google.adk.runners import InMemoryRunner
    from google.genai.types import Content, Part

    current_session_id = "creative_story_session"
    current_user_id = "creative_writer_user"
    runner = InMemoryRunner(agent=creative_writer_agent, app_name="CreativeApp")
    
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

    user_prompt = Content(parts=[Part(text="A brave squirrel on a quest to find the legendary golden acorn.")], role="user")
    print("Creative Writer Story:")
    
    for event in runner.run(user_id=current_user_id, session_id=current_session_id, new_message=user_prompt):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: print(part.text, end="")
    print()

