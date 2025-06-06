from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.google_api_tool.google_api_toolsets import CalendarToolset # Pre-packaged
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os

from building_intelligent_agents.utils import create_session, load_environment_variables, DEFAULT_LLM

# For Google API tools, you'll need OAuth 2.0 Client ID and Secret
# Get these from Google Cloud Console -> APIs & Services -> Credentials
# Ensure your OAuth consent screen is configured and you've added necessary scopes
# (e.g., <https://www.googleapis.com/auth/calendar.events.readonly> for listing events)
GOOGLE_CLIENT_ID = os.getenv("CALENDAR_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("CALENDAR_OAUTH_CLIENT_SECRET")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("Error: CALENDAR_OAUTH_CLIENT_ID and CALENDAR_OAUTH_CLIENT_SECRET env vars must be set.")
    exit()

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    calendar_tools = CalendarToolset(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        # Example filter: only expose tools to list events and get a specific event
        tool_filter=["calendar_events_list", "calendar_events_get"]
    )

    calendar_agent = Agent(
        name="calendar_assistant",
        model=DEFAULT_LLM,
        instruction="You are a helpful Google Calendar assistant. "
                    "When the user refers to 'my calendar' or 'my primary calendar', "
                    "you should use the special calendarId 'primary'. "
                    "Use the tools to manage calendar events.",
        tools=[calendar_tools]
    )

if __name__ == "__main__":
    if not calendar_agent:
        print("Skipping Google Calendar agent example due to missing OAuth credentials.")
    else:
        runner = InMemoryRunner(agent=calendar_agent, app_name="CalendarApp")
        # This will likely trigger an OAuth flow the first time in the Dev UI.
        # The Dev UI has mechanisms to help guide you through this.
        # For command-line, handling the full OAuth redirect flow is complex
        # and often requires a web server component for the redirect URI.
        # The Dev UI simplifies this for local development.
        prompt = "What are the next 3 events on my primary calendar?"
        print(f"\\nYOU: {prompt}")
        # ... (runner and event processing logic) ...
        # This interaction is best tested by running `adk web .` in the parent directory 
        # Make sure you have correctly set up the CALENDAR_OAUTH_CLIENT_ID and CALENDAR_OAUTH_CLIENT_SECRET variables, 
        # preferably through a .env file, otherwise the agent won't initialize properly.

        print("ASSISTANT: (This example is best run with `adk web .` to handle the OAuth flow)")
        print("  The Dev UI will guide you through authorizing access to your Google Calendar.")