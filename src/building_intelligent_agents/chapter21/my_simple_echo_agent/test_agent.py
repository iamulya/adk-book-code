from google.cloud import aiplatform
from vertexai.preview import reasoning_engines

# --- Configuration ---
PROJECT_ID = "<your-gcp-project-id>"  # Replace with your Project ID
LOCATION = "<your-gcp-region>"      # Replace with the region of your Agent Engine
RESOURCE_NUMERIC_ID = "<numeric_id_from_full_resource_name>" # The numeric ID part from the full resource name
REASONING_ENGINE_ID = "projects/{}/locations/{}/reasoningEngines/{}".format(
    PROJECT_ID,
    LOCATION,
    RESOURCE_NUMERIC_ID 
)

# --- Initialize Vertex AI SDK ---
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# --- Get the Reasoning Engine instance ---
# This represents your deployed ADK application
try:
    engine = reasoning_engines.ReasoningEngine(REASONING_ENGINE_ID)
    print(f"Successfully connected to Reasoning Engine: {engine.resource_name}")
except Exception as e:
    print(f"Error connecting to Reasoning Engine: {e}")
    exit()


APP_NAME_FOR_QUERY = "my_simple_echo_agent" # This should match your agent's folder name
USER_ID = "test-user-sdk"

async def test_agent():

    try:
        remote_session = engine.create_session(user_id=USER_ID, app_name=APP_NAME_FOR_QUERY)

        for event_dict in engine.stream_query(
            user_id=USER_ID,
            session_id=remote_session["id"],
            message="whats the weather in new york",
        ):
                # You can deserialize these back into ADK Event objects if needed,
                # but for simple display, printing the dict is fine.
                print(f"  Event Author: {event_dict.get('author')}")
                if event_dict.get("content") and event_dict["content"].get("parts"):
                    for part in event_dict["content"]["parts"]:
                        if part.get("text"):
                            print(f"    Text: {part['text']}")
                        if part.get("functionCall"):
                            print(f"    Function Call: {part['functionCall']['name']}({part['functionCall']['args']})")
                print("-" * 20)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent())