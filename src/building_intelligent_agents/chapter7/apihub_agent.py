from google.adk.agents import Agent
from google.adk.tools.apihub_tool import APIHubToolset # Key import
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os
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

if not APIHUB_RESOURCE_NAME:
    print("Error: MY_APIHUB_API_RESOURCE_NAME environment variable must be set.")
    # exit()

if APIHUB_RESOURCE_NAME:
    # You might need to provide `access_token` or `service_account_json`
    # to APIHubToolset for it to authenticate with the API Hub service,
    # depending on your environment's default credentials.
    # For local dev with `gcloud auth application-default login`, it might work without explicit creds.
    try:
        apihub_toolset = APIHubToolset(
            apihub_resource_name=APIHUB_RESOURCE_NAME,
            # Optional: provide auth for the *target API itself* if needed
            # auth_scheme=some_api_auth_scheme,
            # auth_credential=some_api_auth_credential
        )

        apihub_connected_agent = Agent(
            name="apihub_connector",
            model=DEFAULT_LLM,
            instruction="You can interact with our company's custom API, registered in API Hub. Use the available tools.",
            tools=[apihub_toolset]
        )

        if __name__ == "__main__":
            runner = InMemoryRunner(agent=apihub_connected_agent, app_name="APIHubApp")
            user_id = "apihub_user"
            session_id = "s_apihub"
            create_session(runner, session_id, user_id)

            prompt = "List all customers using our API from API Hub." # Example prompt
            print(f"\\nYOU: {prompt}")
            # ... (rest of the runner logic as in previous examples) ...
            # This assumes 'list_all_customers' is an operationId in the fetched spec.
            # The actual prompt would depend on the tools generated from YOUR API spec.

    except Exception as e:
        print(f"Could not initialize APIHubToolset (ensure API is in Hub and auth is set): {e}")
        apihub_connected_agent = None # Agent not created if toolset fails

else:
    print("Skipping APIHubToolset example as MY_APIHUB_API_RESOURCE_NAME is not set.")
    apihub_connected_agent = None