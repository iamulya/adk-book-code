from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.google_api_tool.google_api_toolsets import CalendarToolset # Pre-packaged
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os

# can't use `from ...utils import load_environment_variables` here because of top-level import error.
def load_environment_variables():
    """
    Load environment variables from a .env file located in the parent directory of the current script.
    """
    # Ensure the .env file is loaded from the parent directory
    # Get the directory of the current script
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the .env file in the parent directory
    dotenv_path = os.path.join(current_script_dir, ".env")

    # Load the .env file if it exists
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Loaded environment variables from: {dotenv_path}")
    else:
        print(f"Warning: .env file not found at {dotenv_path}")
        
load_environment_variables()

# For Google API tools, you'll need OAuth 2.0 Client ID and Secret
# Get these from Google Cloud Console -> APIs & Services -> Credentials
# Ensure your OAuth consent screen is configured and you've added necessary scopes
# (e.g., <https://www.googleapis.com/auth/calendar.events.readonly> for listing events)
GOOGLE_CLIENT_ID = os.getenv("ADK_GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("ADK_GOOGLE_OAUTH_CLIENT_SECRET")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("Error: ADK_GOOGLE_OAUTH_CLIENT_ID and ADK_GOOGLE_OAUTH_CLIENT_SECRET env vars must be set.")
    exit()

root_agent = None
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    calendar_tools = CalendarToolset(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        # Example filter: only expose tools to list events and get a specific event
        # tool_filter=["calendar_events_list", "calendar_events_get"]
    )

    root_agent = Agent(
        name="calendar_assistant",
        model="gemini-2.0-flash",
        instruction="You are a helpful Google Calendar assistant. Use tools to manage calendar events.",
        tools=[calendar_tools]
    )

if __name__ == "__main__":
    if not root_agent:
        print("Skipping Google Calendar agent example due to missing OAuth credentials.")
    else:
        runner = InMemoryRunner(agent=root_agent, app_name="CalendarApp")
        # This will likely trigger an OAuth flow the first time in the Dev UI.
        # The Dev UI has mechanisms to help guide you through this.
        # For command-line, handling the full OAuth redirect flow is complex
        # and often requires a web server component for the redirect URI.
        # The Dev UI simplifies this for local development.
        prompt = "What are the next 3 events on my primary calendar?"
        print(f"\\nYOU: {prompt}")
        # ... (runner and event processing logic) ...
        # This interaction is best tested by running `adk web .` in the parent directory (tools_examples))
        # Make sure you have correctly set up the GOOGLE_API_KEY, ADK_GOOGLE_OAUTH_CLIENT_ID and ADK_GOOGLE_OAUTH_CLIENT_SECRET variables, 
        # preferably through a .env file, otherwise the agent won't initialize properly.

        # The first time a calendar tool is called, ADK (via ToolAuthHandler)
        # will detect the need for OAuth. It will provide an authorization URL.
        # You'll need to visit this URL in a browser, authenticate, grant permissions,
        # and then you'll be redirected to a URL (often localhost if configured for Dev UI).
        # The Dev UI helps capture the authorization code from this redirect.
        # This code is then sent back to the agent (as if it's a user message or a special event).
        # ADK then exchanges this code for an access token, which is then used for API calls.
        print("ASSISTANT: (This example is best run with `adk web .` to handle the OAuth flow)")
        print("  The Dev UI will guide you through authorizing access to your Google Calendar.")