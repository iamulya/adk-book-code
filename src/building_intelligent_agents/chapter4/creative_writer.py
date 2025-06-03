
# agent_definitions/creative_writer.py
from google.adk.agents import Agent
from google.genai.types import GenerateContentConfig, SafetySetting, HarmCategory, HarmBlockThreshold
from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM

load_environment_variables()

custom_safety_settings = [
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_NONE),
]

creative_writer_agent = Agent(
    name="creative_writer", model=DEFAULT_LLM, 
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
    
    create_session(runner, current_session_id, current_user_id)

    user_prompt = Content(parts=[Part(text="A brave squirrel on a quest to find the legendary golden acorn.")], role="user")
    print("Creative Writer Story:")
    
    for event in runner.run(user_id=current_user_id, session_id=current_session_id, new_message=user_prompt):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: print(part.text, end="")
    print()

