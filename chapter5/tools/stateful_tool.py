
# tools/stateful_tool.py
from google.adk.tools import FunctionTool, ToolContext 
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from ...utils import load_environment_variables

load_environment_variables()

def get_and_increment_counter(tool_context: ToolContext) -> str:
    """Retrieves a counter from session state, increments it... Args: tool_context: ..."""
    session_counter = tool_context.state.get("session_counter", 0); session_counter += 1
    tool_context.state["session_counter"] = session_counter
    return f"Counter is now: {session_counter}. Invocation: {tool_context.invocation_id}, FuncCall: {tool_context.function_call_id}"

counter_tool = FunctionTool(func=get_and_increment_counter)

stateful_agent = Agent(
    name="stateful_counter_agent", model="gemini-2.0-flash",
    instruction="You have a tool to get and increment a counter. Use it when asked.",
    tools=[counter_tool]
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=stateful_agent, app_name="StatefulApp")
    session_id = "stateful_session_1"
    user_id = "state_user"

    import asyncio
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

    for i in range(3):
        user_message = Content(parts=[Part(text="Increment counter.")], role="user"); print(f"\nYOU: Increment counter. (Turn {i+1})")
        print("AGENT: ", end="", flush=True)
        for event in runner.run(user_id="state_user", session_id=session_id, new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text: print(event.content.parts[0].text, end="")
        print()
        current_session = runner.session_service._get_session_impl(app_name="StatefulApp", user_id=user_id, session_id=session_id)
        print(f"(Session state 'session_counter': {current_session.state.get('session_counter')})")

