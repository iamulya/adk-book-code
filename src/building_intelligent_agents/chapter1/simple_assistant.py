from dotenv import load_dotenv
from google.adk.agents import Agent 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM

load_environment_variables()

simple_assistant_agent = Agent(
    name="simple_assistant_agent",
    model=DEFAULT_LLM,
    instruction="You are a friendly and helpful assistant. Be concise.",
    description="A basic assistant to answer questions.",
)

if __name__ == "__main__":
    print("Initializing Simple Assistant...")
    runner = InMemoryRunner(agent=root_agent, app_name="MySimpleApp")

    current_session_id = "my_first_session"
    current_user_id = "local_dev_user"

    create_session(runner, current_session_id, current_user_id)

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