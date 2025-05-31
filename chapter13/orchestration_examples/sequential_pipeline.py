# orchestration_examples/sequential_pipeline.py
from google.adk.agents import Agent, SequentialAgent # Import SequentialAgent
from google.adk.tools import FunctionTool, ToolContext
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio

from ...utils import load_environment_variables, create_session
load_environment_variables()

# --- Define Sub-Agents for the Pipeline ---

def gather_user_data(name: str, email: str, tool_context: ToolContext) -> dict:
    """Gathers user's name and email and stores it in session state."""
    tool_context.state["user_name_collected"] = name
    tool_context.state["user_email_collected"] = email
    return {"status": "success", "message": f"Data for {name} collected."}

gather_data_tool = FunctionTool(func=gather_user_data)

data_collection_agent = Agent(
    name="data_collector",
    model="gemini-2.0-flash",
    instruction="Your goal is to collect the user's name and email. Use the 'gather_user_data' tool. Ask for name and email if not provided in the initial query.",
    description="Collects user name and email.",
    tools=[gather_data_tool]
)

def validate_email_format(email: str, tool_context: ToolContext) -> dict:
    """Validates the format of an email address."""
    # Simple regex for basic email validation
    import re
    if re.match(r'[\w.-]+@[\w.-]+.\w+', email):
        tool_context.state["email_validated"] = True
        return {"is_valid": True, "email": email}
    else:
        tool_context.state["email_validated"] = False
        return {"is_valid": False, "email": email, "error": "Invalid email format."}

validate_email_tool = FunctionTool(func=validate_email_format)

email_validation_agent = Agent(
    name="email_validator",
    model="gemini-2.0-flash",
    instruction="You will receive an email address, possibly from session state. Your task is to validate its format using the 'validate_email_format' tool. "
                "The email to validate will be in `state['user_email_collected']`. "
                "Confirm the validation result.",
    description="Validates email format.",
    tools=[validate_email_tool]
)
# Note: This agent is instructed to look for state.
# The SequentialAgent makes the state from previous agents available.


def send_welcome_email(tool_context: ToolContext) -> str:
    """Simulates sending a welcome email if validation passed."""
    if tool_context.state.get("email_validated") and tool_context.state.get("user_name_collected"):
        name = tool_context.state["user_name_collected"]
        email = tool_context.state["user_email_collected"]
        # In a real app, this would use an email API
        return f"Welcome email conceptually sent to {name} at {email}."
    return "Could not send welcome email: email not validated or name missing."

send_email_tool = FunctionTool(func=send_welcome_email)

welcome_email_agent = Agent(
    name="welcome_emailer",
    model="gemini-2.0-flash",
    instruction="If the email has been validated (check `state['email_validated']`), "
                "use the 'send_welcome_email' tool to send a welcome message. "
                "Confirm the action.",
    description="Sends a welcome email.",
    tools=[send_email_tool]
)

# --- Define the SequentialAgent ---
user_onboarding_pipeline = SequentialAgent(
    name="user_onboarding_orchestrator",
    description="A pipeline to onboard new users: collect data, validate email, send welcome.",
    sub_agents=[
        data_collection_agent,
        email_validation_agent,
        welcome_email_agent
    ]
)

# --- Running the SequentialAgent ---
if __name__ == "__main__":
    runner = InMemoryRunner(agent=user_onboarding_pipeline, app_name="OnboardingApp")
    session_id = "s_onboard_seq"
    user_id = "new_user_seq"
    create_session(runner, user_id=user_id, session_id=session_id)

    # The initial message will be processed by data_collection_agent first.
    # Then email_validation_agent, then welcome_email_agent.
    initial_prompt = "Onboard user Alice with email alice@example.com"
    print(f"YOU: {initial_prompt}")
    user_message = Content(parts=[Part(text=initial_prompt)], role="user")  # User message to the agent

    async def main():
        final_agent_responses = []
        # The SequentialAgent itself doesn't produce direct textual output from an LLM.
        # It yields events from its sub_agents. We look for the final text from the *last* sub_agent.
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
            print(f"  EVENT from [{event.author}]:")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"    Text: {part.text.strip()}")
                        if event.author == welcome_email_agent.name and not event.get_function_calls() and not event.get_function_responses():
                            final_agent_responses.append(part.text.strip())
                    elif part.function_call:
                        print(f"    Tool Call: {part.function_call.name}({part.function_call.args})")
                    elif part.function_response:
                        print(f"    Tool Response for {part.function_response.name}: {part.function_response.response}")

        print("\n--- Final Output from Pipeline (last agent's text response) ---")
        if final_agent_responses:
            print("SEQUENTIAL_PIPELINE: " + " ".join(final_agent_responses))
        else:
            print("SEQUENTIAL_PIPELINE: No final text output from the last agent.")

        # Inspect final state
        final_session = await runner.session_service.get_session(
            app_name="OnboardingApp", user_id=user_id, session_id=session_id
        )
        print(f"\nFinal session state: {final_session.state}")

    asyncio.run(main())