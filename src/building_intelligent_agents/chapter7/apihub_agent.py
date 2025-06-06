from google.adk.agents import Agent
from google.adk.tools.apihub_tool import APIHubToolset
from google.adk.runners import InMemoryRunner
from google.adk.tools.openapi_tool import RestApiTool
from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
from google.genai.types import Content, Part
import os
import sys
from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM

load_environment_variables()

# This requires:
# 1. `google-cloud-secret-manager` to be installed if using Secret Manager for API Hub client auth.
# 2. Your environment to be authenticated to GCP with permissions to access API Hub
#    and potentially Secret Manager if API Hub client uses it.
#    (e.g., `gcloud auth application-default login`)
# 3. The API to be registered in API Hub.

# Replace with your actual API Hub resource name
# Format: projects/{project}/locations/{location}/apis/{api}
# Or optionally: projects/{project}/locations/{location}/apis/{api}/versions/{version}
# Or even: projects/{project}/locations/{location}/apis/{api}/versions/{version}/specs/{spec}
APIHUB_RESOURCE_NAME = os.getenv("MY_APIHUB_API_RESOURCE_NAME") # e.g., "projects/my-gcp-project/locations/us-central1/apis/my-customer-api"

class PatchedAPIHubToolset(APIHubToolset):
    """
    A patched version of APIHubToolset that manually sets the server URL
    to work around a bug where the base_url or server.url is a relative url.
    """
    def __init__(self, *args, **kwargs):
        # Allow passing a custom base_url
        self.override_base_url = kwargs.pop("override_base_url", None)
        super().__init__(*args, **kwargs)

    async def get_tools(self, readonly_context=None) -> list[RestApiTool]:
        # Get the tools from the parent class
        tools = await super().get_tools(readonly_context)

        if self.override_base_url:
            print(f"🔧 Applying patch: Overriding base URL for all tools with '{self.override_base_url}'")
            for tool in tools:
                # Manually set the base_url on the tool's endpoint
                tool.endpoint.base_url = self.override_base_url
        return tools

def is_valid_adk_tool(tool: RestApiTool, ctx=None) -> bool:
    """
    A filter to exclude tools that the ADK parser cannot handle correctly.

    The ADK's OpenApiSpecParser currently creates a tool parameter with an
    empty name if the requestBody is not a JSON object. This causes a
    `400 INVALID_ARGUMENT` error from the Gemini API.

    This filter identifies and excludes such tools.
    """
    operation = tool._operation_parser._operation
    if not operation.requestBody or not operation.requestBody.content:
        # No request body, so it's a valid tool (e.g., GET with params in URL)
        return True

    # Check the first content type (usually 'application/json')
    for media_type in operation.requestBody.content.values():
        if media_type.schema_ and media_type.schema_.type != 'object':
            # This is the problematic case: a body that isn't a named object.
            print(f"Filtering out tool '{tool.name}' due to non-object requestBody (type: {media_type.schema_.type}).")
            return False

    # If all checks pass, the tool is considered valid.
    return True

apihub_connected_agent = None

if not APIHUB_RESOURCE_NAME:
    print("Error: MY_APIHUB_API_RESOURCE_NAME environment variable must be set.", file=sys.stderr)
else:
    try:
        petstore_auth_scheme, petstore_auth_credential = token_to_scheme_credential(
            token_type="apikey",
            location="header",
            name="api_key", # This must match the name in the OpenAPI spec's security scheme
            credential_value="special-key"
        )

        # Apply the filter and the auth config when creating the toolset
        # Use the new PatchedAPIHubToolset class
        apihub_toolset = PatchedAPIHubToolset(
            apihub_resource_name=APIHUB_RESOURCE_NAME,
            tool_filter=is_valid_adk_tool,
            auth_scheme=petstore_auth_scheme,
            auth_credential=petstore_auth_credential,
            # Provide the correct server URL here
            override_base_url="https://petstore3.swagger.io/api/v3"
        )

        apihub_connected_agent = Agent(
            name="apihub_connector",
            model=DEFAULT_LLM,
            instruction="You can interact with our APIs, registered in API Hub. Use the available tools.",
            tools=[apihub_toolset]
        )
        print("APIHubToolset and Agent initialized successfully.")

    except Exception as e:
        print(f"Could not initialize APIHubToolset. Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if not apihub_connected_agent:
        print("Agent could not be created. Exiting.", file=sys.stderr)
        sys.exit(1)

    runner = InMemoryRunner(agent=apihub_connected_agent, app_name="APIHubApp")
    user_id = "apihub_user"
    session_id = "s_apihub"
    create_session(runner, session_id, user_id)

    prompt_text = "Can you add a new pet named 'Buddy' with status 'available' and id 12345?"
    print(f"\nYOU: {prompt_text}")

    async def main():
        user_message = Content(parts=[Part(text=prompt_text)], role="user")
        print("PETSTORE_MANAGER: ", end="", flush=True)

        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        print()

    import asyncio
    asyncio.run(main())