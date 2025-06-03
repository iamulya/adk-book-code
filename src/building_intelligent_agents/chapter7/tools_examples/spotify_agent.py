# single_spotify_agent_runner.py
import asyncio

from google.adk.agents import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset
from google.adk.auth import AuthCredential, AuthCredentialTypes
from fastapi.openapi.models import APIKey, APIKeyIn
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

# --- Spotify OpenAPI Spec (Simplified) ---
SPOTIFY_API_SPEC_STR = """
openapi: 3.0.0
info:
  title: Spotify Web API (Simplified for ADK Demo)
  version: v1
  description: Subset of Spotify Web API for searching tracks.
servers:
  - url: https://api.spotify.com/v1
components:
  securitySchemes:
    SpotifyApiKeyAuth: # This name must match the name used in the global `security` or operation-level `security` section
      type: apiKey
      in: header # Can be 'header', 'query', or 'cookie'
      name: Authorization # This is the header Spotify expects for Bearer tokens
security:
  - SpotifyApiKeyAuth: [] # Applies ApiKeyAuth globally to all operations
paths:
  /search:
    get:
      summary: Search for an Item
      operationId: searchForItem # This will become the tool name (search_for_item)
      description: |
        Get Spotify catalog information about artists, albums, tracks or playlists
        that match a keyword string.
      parameters:
        - name: q
          in: query
          description: "Search query keywords and optional field filters and operators. Example: 'track:The Sign artist:Ace of Base'"
          required: true
          schema:
            type: string
        - name: type
          in: query
          description: "A comma-separated list of item types to search across. Valid types are: album, artist, playlist, track, show, episode, audiobook."
          required: true
          schema:
            type: string
        - name: market
          in: query
          description: "An ISO 3166-1 alpha-2 country code. If a market is given, only content playable in that market will be returned."
          required: false
          schema:
            type: string
        - name: limit
          in: query
          description: "Maximum number of results to return. Default: 20. Minimum: 1. Maximum: 50."
          required: false
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 50
        - name: offset
          in: query
          description: "The index of the first result to return. Default: 0 (the first result). Maximum offset: 100,000. Use with limit to get the next page of search results."
          required: false
          schema:
            type: integer
            default: 0
      responses:
        '200':
          description: Search results.
          content:
            application/json:
              schema:
                type: object # A more complete spec would detail the response structure
                properties:
                  tracks:
                    type: object
                    properties:
                      items:
                        type: array
                        items:
                          type: object
                          properties:
                            name:
                              type: string
                            artists:
                              type: array
                              items:
                                type: object
                                properties:
                                  name:
                                    type: string
                            album:
                              type: object
                              properties:
                                name:
                                  type: string
                            external_urls:
                              type: object
                              properties:
                                spotify:
                                  type: string
                  # ... other types like artists, albums, etc.
        '400':
          description: Bad request.
        '401':
          description: Bad or expired token. This can happen if the user revoked a token or the access token has expired. You should re-authenticate the user.
        '403':
          description: Bad OAuth request (wrong consumer key, bad nonce, expired timestamp...). Unfortunately, re-authenticating the user won't help here.
        '429':
          description: The app has exceeded its rate limits.
"""

# --- Authentication Setup ---
# IMPORTANT: You need a Spotify Access Token for this to work.
# 1. Go to https://developer.spotify.com/dashboard/ and create an app.
# 2. Get your Client ID and Client Secret.
# 3. Use the Client Credentials Flow to obtain an Access Token.
#    A simple way to do this is with curl:
#    curl -X "POST" -H "Authorization: Basic <BASE64_ENCODED_CLIENT_ID:CLIENT_SECRET>" -d grant_type=client_credentials https://accounts.spotify.com/api/token
#    (Replace <BASE64_ENCODED_CLIENT_ID:CLIENT_SECRET> with your actual base64 encoded "client_id:client_secret" string)
# 4. The response will contain an "access_token". Prepend "Bearer " to it.
#
# For this example, we'll treat the "Bearer <ACCESS_TOKEN>" string as our "API Key".
SPOTIFY_BEARER_TOKEN = "Bearer YOUR_SPOTIFY_ACCESS_TOKEN"  # <<< REPLACE THIS!


# Define the API Key authentication scheme.
# This MUST match how `SpotifyApiKeyAuth` is defined in your OpenAPI spec's `components.securitySchemes`.
spotify_api_key_auth_scheme = APIKey(
    type="apiKey",
    name="Authorization",    # This is the header name Spotify expects
    in_=APIKeyIn.header
)

# Create the AuthCredential. The `api_key` value will be the full "Bearer <token>" string.
spotify_api_key_credential = AuthCredential(
    auth_type=AuthCredentialTypes.API_KEY,
    api_key=SPOTIFY_BEARER_TOKEN
)

# --- Toolset Setup ---
# Initialize the OpenAPIToolset.
spotify_toolset = OpenAPIToolset(
    spec_str=SPOTIFY_API_SPEC_STR,
    spec_str_type="yaml", # The spec string is in YAML format
    auth_scheme=spotify_api_key_auth_scheme,
    auth_credential=spotify_api_key_credential
)

# --- Agent Definition ---
spotify_agent = Agent(
    name="SpotifySearchAgent",
    model=DEFAULT_LLM, 
    instruction=(
        "You are a Spotify music search assistant. "
        "Use the 'searchForItem' tool to find tracks, artists, or albums on Spotify. "
        "When searching, you must specify the 'type' parameter (e.g., 'track', 'artist', 'album'). "
        "If the user asks to search for a song, use type 'track'. "
        "After getting results, list the names of up to 3 found items. "
        "If searching for tracks, also include the artist and album name if available."
    ),
    tools=[
        spotify_toolset
    ]
)

# --- Example of running this agent ---
if __name__ == "__main__":
    if "YOUR_SPOTIFY_ACCESS_TOKEN" in SPOTIFY_BEARER_TOKEN:
        print("="*80)
        print("!!! IMPORTANT WARNING !!!")
        print("It appears 'YOUR_SPOTIFY_ACCESS_TOKEN' might still be the placeholder")
        print("in the SPOTIFY_BEARER_TOKEN variable in this script.")
        print("The agent will likely fail to authenticate with the Spotify API.")
        print("Please update it with your actual Spotify Bearer token and try again.")
        print("See comments in the script for details on obtaining a token.")
        print("="*80)
        
        exit(1)

    runner = InMemoryRunner(agent=spotify_agent, app_name="SpotifySearchAppSingleFile")

    user_id = "spotify_user"
    session_id = "s_spotify"
    create_session(runner, session_id, user_id)

    # Selected prompts for testing
    prompts = [
        "Find the song 'Stairway to Heaven'.",
        "Search for artists named 'Queen'.",
        "Can you find albums by 'Daft Punk'?",
        "What tracks are there by an artist named 'Lorde'?",
        "Search for the track 'Bohemian Rhapsody' by Queen.",
        "search for item q='Never Gonna Give You Up' type='track' limit=1"
    ]

    async def main_loop():
        # Create session once before the loop
        await create_session(runner, session_id, user_id)
        print("-" * 70)

        for prompt_text in prompts:
            print(f"\nYOU: {prompt_text}")
            user_message = Content(parts=[Part(text=prompt_text)], role="user")
            print(f"{spotify_agent.name.upper()}: ", end="", flush=True)

            # Use run_async as we are in an async main function
            async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=user_message
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
            print("\n" + "-" * 70) # Separator for readability
            # Optional: Add a small delay if you're making many API calls in a loop
            await asyncio.sleep(1) # Helps avoid hitting rate limits if prompts are processed very fast

    asyncio.run(main_loop())