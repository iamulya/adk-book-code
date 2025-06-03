# session_state_examples/scoped_state_demo.py
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, ToolContext
from google.adk.runners import InMemoryRunner
from google.adk.sessions.state import State # For prefix constants
from google.genai.types import Content, Part
import asyncio

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()  # Load environment variables for ADK configuration

def manage_preferences(tool_context: ToolContext, theme: str, language: str = "") -> dict:
    """Sets or gets user and app preferences."""
    changes = {}
    if theme:
        tool_context.state[State.USER_PREFIX + "theme"] = theme # user:theme
        changes["user_theme_set"] = theme
    if language:
        tool_context.state[State.APP_PREFIX + "default_language"] = language # app:default_language
        changes["app_language_set"] = language

    # Example of session-specific state
    tool_context.state["last_preference_tool_call_id"] = tool_context.function_call_id
    # Example of temporary state
    tool_context.state[State.TEMP_PREFIX + "last_tool_name"] = "manage_preferences"

    return {
        "status": "Preferences updated.",
        "changes_made": changes,
        "current_user_theme": tool_context.state.get(State.USER_PREFIX + "theme"),
        "current_app_language": tool_context.state.get(State.APP_PREFIX + "default_language"),
        "session_specific_info": tool_context.state.get("last_preference_tool_call_id")
    }

preference_tool = FunctionTool(func=manage_preferences)

state_demo_agent = Agent(
    name="preference_manager",
    model=DEFAULT_LLM,
    instruction="Manage user and application preferences using the 'manage_preferences' tool. "
                "You can set a user's theme or the app's default language.",
    tools=[preference_tool]
)

if __name__ == "__main__":
    # Using InMemorySessionService for this demo.
    # Scoped state behavior is fully realized with persistent services like DatabaseSessionService.
    runner = InMemoryRunner(agent=state_demo_agent, app_name="PrefsDemo")

    user1_id = "user_alpha"
    user2_id = "user_beta"
    session1_user1_id = "s1_alpha"
    session2_user1_id = "s2_alpha" # Different session for same user
    session1_user2_id = "s1_beta"

    create_session(runner, user_id=user1_id, session_id=session1_user1_id)
    create_session(runner, user_id=user1_id, session_id=session2_user1_id)
    create_session(runner, user_id=user2_id, session_id=session1_user2_id)

    async def run_and_print_state(user_id: str, session_id: str, prompt: str, app_name="PrefsDemo"):
        print(f"\\n--- Running for User: {user_id}, Session: {session_id} ---")
        print(f"YOU: {prompt}")
        user_message = Content(parts=[Part(text=prompt)], role="user")
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.author == state_demo_agent.name and event.content and event.content.parts[0].text:
                 if not event.get_function_calls() and not event.get_function_responses():
                    print(f"AGENT: {event.content.parts[0].text.strip()}")

        # Inspect state after the run
        # With InMemorySessionService, app and user scopes are emulated within its single dict.
        # DatabaseSessionService would store them in separate tables.
        s = await runner.session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
        print(f"  Session State for {session_id}: { {k:v for k,v in s.state.items() if not (k.startswith(State.APP_PREFIX) or k.startswith(State.USER_PREFIX))} }")
        print(f"  User-Scoped State for {user_id} (via session merge): { {k:v for k,v in s.state.items() if k.startswith(State.USER_PREFIX)} }")
        print(f"  App-Scoped State for {app_name} (via session merge): { {k:v for k,v in s.state.items() if k.startswith(State.APP_PREFIX)} }")
        print(f"  Temp state (would not persist in DB): { {k:v for k,v in s.state.items() if k.startswith(State.TEMP_PREFIX)} }")

    async def main():

        # User Alpha, Session 1: Set theme and app language
        await run_and_print_state(user1_id, session1_user1_id, "Set my theme to 'dark' and app language to 'English'.")

        # User Alpha, Session 2: Check theme (should persist for user) and app language (should persist for app)
        await run_and_print_state(user1_id, session2_user1_id, "What's my theme and the app language?")

        # User Beta, Session 1: Set their theme, check app language (should be what Alpha set)
        await run_and_print_state(user2_id, session1_user2_id, "Set my theme to 'light'. What's the app language?")

        # User Alpha, Session 1 (again): Check theme (should still be dark)
        await run_and_print_state(user1_id, session1_user1_id, "Just checking my theme again.")

    asyncio.run(main())