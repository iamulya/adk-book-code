
# main.py
import os
from google.adk.agents import Agent 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

if not os.getenv("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()
root_agent = Agent(
    name="simple_assistant", model="gemini-1.5-flash-latest", 
    instruction="You are a friendly and helpful assistant. Be concise.",
    description="A basic assistant to answer questions.",
)
if __name__ == "__main__":
    print("Initializing Simple Assistant...")
    runner = InMemoryRunner(agent=root_agent, app_name="MySimpleApp")
    print("Simple Assistant is ready. Type 'exit' to quit.")
    current_session_id = "my_first_session"; current_user_id = "local_dev_user"
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit': print("Exiting Simple Assistant. Goodbye!"); break
        if not user_input.strip(): continue
        user_message = Content(parts=[Part(text=user_input)], role="user") 
        print("Assistant: ", end="", flush=True)
        try:
            for event in runner.run(
                user_id=current_user_id, session_id=current_session_id, new_message=user_message,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text: print(part.text, end="", flush=True)
            print() 
        except Exception as e:
            print(f"\nAn error occurred: {e}")

