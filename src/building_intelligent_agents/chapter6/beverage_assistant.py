import asyncio
from google.genai.types import Content, Part, FunctionResponse

from google.adk.agents import Agent
from google.adk.tools import get_user_choice
from google.adk.runners import InMemoryRunner

from building_intelligent_agents.utils import load_environment_variables, DEFAULT_LLM
load_environment_variables()

instruction = (
    "You are a helpful beverage assistant. "
    "First, ask the user to choose between 'coffee' and 'tea' using the get_user_choice tool. "
    "After the user makes a choice, confirm their selection by saying 'You chose [their choice]! Excellent!'"
)

beverage_assistant = Agent(
    name="beverage_assistant",
    model=DEFAULT_LLM,
    instruction=instruction,
    tools=[get_user_choice],
)

runner = InMemoryRunner(agent=beverage_assistant)


async def main():
    """Simulates a multi-turn conversation with the agent."""
    user_id = "test_user"
    session_id = "test_session_1234"

    await runner.session_service.create_session(
        app_name=runner.app_name, user_id=user_id, session_id=session_id
    )

    # --- Turn 1: User starts the conversation ---
    print("--- Turn 1: User starts the conversation ---")
    user_message = "I'm thirsty, what are my options?"
    print(f"[user]: {user_message}\n")

    function_call_id = None
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=Content(parts=[Part(text=user_message)]),
    ):
        print(f"  [event from agent]: {event.author} -> {event.content.parts if event.content else 'No Content'}")
        if calls := event.get_function_calls():
            options = calls[0].args.get("options", [])
            function_call_id = calls[0].id
            print(
                f"  [system]: Agent wants to call get_user_choice with ID: {function_call_id}"
            )
            print(f"  [system]: The UI would now show the user these options: {options}\n")

    if not function_call_id:
        print("Error: Agent did not call the get_user_choice tool as expected.")
        return

    # --- Turn 2: Simulate the user making a choice ---
    user_choice = "coffee"
    print(f"--- Turn 2: User chooses '{user_choice}' ---")

    # Create the function response object first, ensuring the ID is set
    func_resp = FunctionResponse(
        name="get_user_choice",
        response={"result": user_choice},
        id=function_call_id  # This correctly sets the ID
    )

    # Now create the Part from the FunctionResponse object
    response_part = Part(function_response=func_resp)

    # Create and add an empty text part to satisfy the Gemini API which expects a text Part for "user" Content
    empty_text_part = Part(text="")

    # Create the final content message to send to the agent
    function_response_content = Content(
        role="user", # Function responses are sent back as the 'user'
        parts=[empty_text_part,response_part],
    )

    print(
        f"[user function_response]: name='get_user_choice', response={{'result': '{user_choice}'}}\n"
    )

    # --- Turn 3: Agent processes the choice and responds ---
    print("--- Turn 3: Agent confirms the choice ---")
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=function_response_content,
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"[{event.author}]: {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())