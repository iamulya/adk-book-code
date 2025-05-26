
# agent_definitions/dynamic_greeter.py
import os
from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext 
from datetime import datetime
from ...utils import load_environment_variables

load_environment_variables()

def get_time_based_greeting_instruction(context: ReadonlyContext) -> str:
    current_hour = datetime.now().hour
    user_name = context.state.get("user:user_name", "there") 
    if 5 <= current_hour < 12: greeting_time = "morning"
    elif 12 <= current_hour < 18: greeting_time = "afternoon"
    else: greeting_time = "evening"
    return f"You are a cheerful assistant. Greet the user '{user_name}' and wish them a good {greeting_time}. Then, ask how you can help."

dynamic_greeter_agent = Agent(
    name="dynamic_greeter", model="gemini-2.0-flash",
    instruction=get_time_based_greeting_instruction, 
    description="Greets the user dynamically based on the time of day and their name."
)

if __name__ == "__main__":
    from google.adk.runners import InMemoryRunner
    from google.genai.types import Content, Part
    runner = InMemoryRunner(agent=dynamic_greeter_agent, app_name="DynamicApp")
    user_id = "jane_doe"; session_id = "session_greet_jane"; initial_state = {"user:user_name": "Jane"}
    runner.session_service._create_session_impl(app_name="DynamicApp", user_id=user_id, session_id=session_id, state=initial_state)
    user_message = Content(parts=[Part(text="Hello")])
    print(f"Running dynamic_greeter_agent for user: {user_id}...")
    for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: print(part.text, end="")
    print()

