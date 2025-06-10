from google.adk.agents import Agent
from google.adk.tools import load_artifacts # To access it later
from google.adk.runners import InMemoryRunner, RunConfig # Import RunConfig
from google.genai.types import Content, Part, Blob
import asyncio

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()  # Load environment variables for ADK configuration

upload_processor_agent = Agent(
    name="upload_processor",
    model=DEFAULT_LLM,
    instruction="You will receive information about uploaded files. If asked about an uploaded file, use 'load_artifacts' to get its content and then describe it.",
    tools=[load_artifacts]
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=upload_processor_agent, app_name="UploadApp")
    session_id = "s_upload_test"
    user_id = "upload_user"
    create_session(runner, user_id=user_id, session_id=session_id)  # Create a session for the user

    # Create a message with an inline_data part (simulating a user upload)
    dummy_text_data = "This is the content of my uploaded file."
    user_uploaded_file_part = Part(inline_data=Blob(mime_type="text/plain", data=dummy_text_data.encode()))
    user_query_part = Part(text="I've uploaded a file. Can you tell me what it is?")
    message_with_upload = Content(parts=[user_query_part, user_uploaded_file_part])

    # Configure RunConfig to save blobs
    config_save_blobs = RunConfig(save_input_blobs_as_artifacts=True)

    async def main():
        print(f"\n--- Running with save_input_blobs_as_artifacts=True ---")
        print(f"Original user message parts: {len(message_with_upload.parts)}")
        print(f"YOU (conceptually with upload): {user_query_part.text}")

        print("AGENT: ", end="", flush=True)
        async for event in runner.run_async(
            user_id="upload_user",
            session_id=session_id,
            new_message=message_with_upload,
            run_config=config_save_blobs
        ):
            # The agent will first see "Uploaded file: artifact_..."
            # Then it should call load_artifacts for that artifact name.
            # Then it will respond based on the content.
            if event.content and event.content.parts[0].text and not event.get_function_calls():
                print(event.content.parts[0].text.strip())

        # Verify the artifact was saved by the Runner
        artifacts = await runner.artifact_service.list_artifact_keys(app_name="UploadApp", user_id=user_id, session_id=session_id)
        print(f"  [DEBUG] Artifacts created by Runner: {artifacts}")
        assert len(artifacts) == 1

        # Verify content
        # loaded_artifact = await runner.artifact_service.load_artifact("UploadApp", "upload_user", session_id, artifacts[0])
        # assert loaded_artifact.inline_data.data.decode() == dummy_text_data

    asyncio.run(main())
