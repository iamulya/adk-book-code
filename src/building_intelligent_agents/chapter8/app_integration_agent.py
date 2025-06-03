# tools_examples/app_integration_agent.py
# This is a conceptual example, as it requires a configured Application Integration.
from google.adk.agents import Agent
from google.adk.tools.application_integration_tool import ApplicationIntegrationToolset
# from google.adk.runners import InMemoryRunner
# from google.genai.types import Content, Part
import os
# from ...utils import load_environment_variables, create_session, DEFAULT_LLM
# load_environment_variables()

GCP_PROJECT_AI = os.getenv("GOOGLE_CLOUD_PROJECT") # Your GCP Project
GCP_LOCATION_AI = os.getenv("APP_INTEGRATION_LOCATION", "us-central1")
# Name of your deployed integration with an API trigger
INTEGRATION_NAME = os.getenv("MY_APP_INTEGRATION_NAME")
# Trigger ID from your integration's API trigger
TRIGGER_ID = os.getenv("MY_APP_INTEGRATION_TRIGGER_ID")
# Path to your service account JSON key file with permissions for App Integration
SERVICE_ACCOUNT_JSON_PATH_AI = os.getenv("APP_INTEGRATION_SA_KEY_PATH")

app_integration_agent = None
if all([GCP_PROJECT_AI, GCP_LOCATION_AI, INTEGRATION_NAME, TRIGGER_ID]):
    sa_json_content_ai = None
    if SERVICE_ACCOUNT_JSON_PATH_AI and os.path.exists(SERVICE_ACCOUNT_JSON_PATH_AI):
        with open(SERVICE_ACCOUNT_JSON_PATH_AI, 'r') as f:
            sa_json_content_ai = f.read()
    elif SERVICE_ACCOUNT_JSON_PATH_AI: # Path provided but not found
        print(f"Warning: Service account key file not found at {SERVICE_ACCOUNT_JSON_PATH_AI}")


    try:
        # Example: Toolset for a specific integration trigger
        app_int_toolset = ApplicationIntegrationToolset(
            project=GCP_PROJECT_AI,
            location=GCP_LOCATION_AI,
            integration=INTEGRATION_NAME,
            triggers=[TRIGGER_ID], # List of trigger IDs
            service_account_json=sa_json_content_ai # Can be None to use ADC
        )

        # Example: Toolset for an Integration Connector (e.g., Salesforce)
        # Assume 'my_salesforce_connection' is a configured connector
        # and it supports 'Account' entity with 'GET' and 'LIST' operations.
        # app_int_connector_toolset = ApplicationIntegrationToolset(
        #     project=GCP_PROJECT_AI,
        #     location=GCP_LOCATION_AI,
        #     connection="my_salesforce_connection",
        #     entity_operations={"Account": ["GET", "LIST"]},
        #     service_account_json=sa_json_content_ai
        # )

        app_integration_agent = Agent(
            name="enterprise_gateway_agent",
            model=DEFAULT_LLM,
            instruction="You can trigger enterprise workflows via Application Integration.",
            tools=[app_int_toolset] # Add the toolset
        )
        print("ApplicationIntegrationToolset initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize ApplicationIntegrationToolset: {e}")
        print("Ensure Application Integration is set up and SA has permissions.")

else:
    print("Skipping ApplicationIntegrationToolset example due to missing environment variables.")


if __name__ == "__main__":
    if app_integration_agent:
        # runner = InMemoryRunner(agent=app_integration_agent, app_name="AppIntApp")
        # session_id = "s_app_integration_test"
        # user_id = "app_integration_user"
        # create_session(runner, session_id, user_id)

        # ... (runner logic - this would make a call to your specific integration)
        # prompts = [
        #     "Your prompt here to trigger the integration, e.g., 'Create a new account in Salesforce.'",
        #     "Another prompt to trigger a different workflow, e.g., 'List all accounts in Salesforce.'",
        #     # Add more prompts as needed
        # ]
        # for prompt_text in prompts:
        #     print(f"\\nYOU: {prompt_text}")
        #     user_message = Content(parts=[Part(text=prompt_text)], role="user")
        #     print("ASSISTANT: ", end="", flush=True)

        #     for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
        #         if event.content and event.content.parts:
        #             for part in event.content.parts:
        #                 if part.text:
        #                     print(part.text, end="", flush=True)
        
        print("Agent with ApplicationIntegrationToolset created, but actual run is conceptual without a live integration.")
        print("Test with `adk web .` and provide necessary parameters if your integration expects them.")
    else:
        print("ApplicationIntegration agent not created.")