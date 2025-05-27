# tools/user_profile_tool.py
from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from ...utils import load_environment_variables

load_environment_variables()

# Here we use Pydantic to define a model for user profiles. Pydantic sometimes has types like EmailStr that are not known to the LLM.
# If you want to use types like EmailStr, you need to ensure the LLM can understand them by creating a Custom Tool class that manually defines its schema for the LLM.
class UserProfile(BaseModel):
    username: str = Field(description="The username of the user.")
    email: str = Field(description="The email address of the user.") 
    age: int = Field(description="The age of the user.")

def update_user_profile(profile: dict) -> dict:
    """Updates a user's profile information. Args: profile: A UserProfile object..."""
    try:
        # Validate and convert the incoming dictionary to UserProfile instance
        user_profile_instance = UserProfile.model_validate(profile)
    except Exception as e: # Catch PydanticValidationError or other potential errors
        print(f"Error validating profile data: {profile}. Error: {e}")
        return {"status": "error", "message": f"Invalid profile data provided. {e}"}
    
    print(f"Updating profile for {user_profile_instance.username} with email {user_profile_instance.email}")

    # Here you would typically update the profile in a database or some storage.

    return {"status": "success", "updated_username": user_profile_instance.username}

user_profile_updater_tool = FunctionTool(func=update_user_profile)

# Sometimes you have to be specific about the instruction for the tool, especially if the LLM needs to understand how to use it.
# This instruction provider is NOT currently used, but if used, provides clear and concise instructions to the LLM on how to use the tool.
def user_profile_tool_instruction(context: ReadonlyContext) -> str:
    """Generates the instruction for the user profile tool."""
    print(f"User profile schema: {UserProfile.model_json_schema()}")
    return f"""You are a user profile manager. Your task is to call the tool named '{user_profile_updater_tool.name}' "
        The tool expects {UserProfile.model_json_schema()}. 
    """

profile_agent = Agent(
    name="profile_manager",
    model="gemini-2.0-flash",
    instruction="Manage user profiles using the provided tool.",#user_profile_tool_instruction
    tools=[user_profile_updater_tool]
)

if __name__ == "__main__":
    from google.adk.runners import InMemoryRunner
    runner = InMemoryRunner(agent=profile_agent, app_name="ProfileManagerApp")

    user_id="user"
    session_id="profile_session"

    import asyncio
    from google.genai.types import Content, Part
    
    # --- Create the session before the loop ---
    print(f"Creating session: {session_id} for user: {user_id} on app: {runner.app_name}")
    # Since session_service.create_session is async, we need to run it in an event loop
    try:
        asyncio.run(runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        ))
        print("Session created successfully.")
    except Exception as e:
        print(f"Error creating session: {e}")
        exit()
    # --- Session creation done ---
    
    print("\nProfile Manager is ready. Type 'exit' to quit.")
    print("Example prompts:")
    print(" - Update my profile: username is 'testuser', email is 'test@example.com', age is 36")

    # This will test if the agent understands that it requires the age parameter
    print(" - Set user 'janedoe' profile with email 'jane.doe@email.net'.")
    print("-" * 30)

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Exiting Profile Manager. Goodbye!")
            break
        if not user_input.strip():
            continue

        user_message = Content(parts=[Part(text=user_input)], role="user")
        print("Agent: ", end="", flush=True)
        try:
            for event in runner.run(
                user_id=user_id, session_id=session_id, new_message=user_message,
            ):
                if event.content and event.content.parts:
                    # Print tool calls for debugging/visibility
                    if event.get_function_calls():
                        for fc in event.get_function_calls():
                            print(f"\n[AGENT INTENDS TO CALL TOOL] Name: {fc.name}, Args: {fc.args}")
                    # Print tool responses for debugging/visibility
                    if event.get_function_responses():
                         for fr in event.get_function_responses():
                            print(f"\n[TOOL RESPONSE RECEIVED BY AGENT] Name: {fr.name}, Response: {fr.response}")
                    # Print text from the agent
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
            print() # Newline after agent's full response
        except Exception as e:
            print(f"\nAn error occurred: {e}")