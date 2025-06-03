# tools_examples/choice_agent.py
from google.adk.agents import Agent
from google.adk.tools import get_user_choice # The pre-built tool
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

choice_agent = Agent(
    name="choice_resolver_agent",
    model=DEFAULT_LLM,
    instruction=(
        "You are an assistant that helps users make decisions. "
        "If a user's request is ambiguous or has multiple valid interpretations, "
        "formulate a clear question with specific options for the user. "
        "Then, use the 'get_user_choice' tool to present these options and get their selection. "
        "The options should be concise and clearly numbered if possible for the user to select easily. "
        "After the user makes a choice, proceed with their selected option."
    ),
    tools=[get_user_choice] # Add the tool to the agent
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=choice_agent, app_name="ChoiceApp")
    session_id = "s_user_choice"
    user_id="choice_user"
    create_session(runner, session_id, user_id)
    
    print("\nChoice Agent is ready. Type 'exit' to quit.")
    print("Example prompt: I want to book a flight to a sunny destination.")
    print("-" * 30)

    latest_function_call_id_for_choice = None

    while True:
        if latest_function_call_id_for_choice:
            # We are expecting user input for a previous tool call
            user_selection_input = input("Your choice (enter number or text): ")
            if user_selection_input.lower() == 'exit': break

            # This is a simplified way to map back. A real UI would be better.
            # For now, we'll just send back the text the user typed.
            # A more robust system would map the number back to the option text
            # or have the LLM expect the number.
            user_choice_response_part = Part.from_function_response(
                name="get_user_choice",
                id=latest_function_call_id_for_choice,
                response={"result": user_selection_input} # LLM expects result
            )
            user_message = Content(parts=[user_choice_response_part], role="user") # Role is user for tool response
            print("You (Choice): ", user_selection_input)
            latest_function_call_id_for_choice = None # Reset
        else:
            # Normal user prompt
            user_prompt_text = input("You: ")
            if user_prompt_text.lower() == 'exit': break
            if not user_prompt_text.strip(): continue
            user_message = Content(parts=[Part(text=user_prompt_text)], role="user")

        print("Agent: ", end="", flush=True)
        current_turn_function_calls = []
        try:
            for event in runner.run(
                user_id=user_id, session_id=session_id, new_message=user_message,
            ):
                if event.content and event.content.parts:
                    # Check for function calls from the agent
                    if event.get_function_calls():
                        for fc in event.get_function_calls():
                            print(f"\n[AGENT INTENDS TO CALL TOOL] Name: {fc.name}, Args: {fc.args}, ID: {fc.id}")
                            if fc.name == "get_user_choice":
                                current_turn_function_calls.append(fc)
                                # --- UI Logic to display options ---
                                print("\nAgent wants you to choose:")
                                options_from_llm = fc.args.get("options", [])
                                for i, option in enumerate(options_from_llm):
                                    print(f"  {i+1}. {option}")
                                # --- End UI Logic ---

                    # Print text parts
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
            print()

            # After the turn, if get_user_choice was called, set up to get user's choice
            if current_turn_function_calls:
                # Assuming only one get_user_choice call per turn for simplicity here
                fc_for_choice = next((fc for fc in current_turn_function_calls if fc.name == "get_user_choice"), None)
                if fc_for_choice:
                    latest_function_call_id_for_choice = fc_for_choice.id
                else: # Should not happen if UI logic was triggered
                    latest_function_call_id_for_choice = None
            else:
                latest_function_call_id_for_choice = None

        except Exception as e:
            print(f"\nAn error occurred: {e}")
            latest_function_call_id_for_choice = None # Reset on error