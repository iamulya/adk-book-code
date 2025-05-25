
# agent_definitions/creative_writer.py
from google.adk.agents import Agent
from google.genai.types import GenerateContentConfig, SafetySetting, HarmCategory
custom_safety_settings = [
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
]
creative_writer_agent = Agent(
    name="creative_writer", model="gemini-1.5-pro-latest", 
    instruction="You are a creative writer. Write a short, imaginative story based on the user's prompt.",
    description="Generates short creative stories.",
    generate_content_config=GenerateContentConfig(
        temperature=0.9, top_p=0.95, top_k=40, max_output_tokens=512, safety_settings=custom_safety_settings
    )
)
if __name__ == "__main__":
    from google.adk.runners import InMemoryRunner
    from google.genai.types import Content, Part
    runner = InMemoryRunner(agent=creative_writer_agent, app_name="CreativeApp")
    user_prompt = Content(parts=[Part(text="A brave squirrel on a quest to find the legendary golden acorn.")])
    print("Creative Writer Story:")
    for event in runner.run(user_id="writer_user", session_id="story_time", new_message=user_prompt):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: print(part.text, end="")
    print()

