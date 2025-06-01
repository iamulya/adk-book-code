# artifacts_examples/in_memory_artifact_demo.py
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, ToolContext
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part, Blob
import asyncio # For async tool function

from ...utils import load_environment_variables, create_session
load_environment_variables()  # Load environment variables for ADK configuration

# Tool to create and save an artifact
async def create_and_save_text_artifact(filename: str, content_text: str, tool_context: ToolContext) -> dict:
    """Creates a text artifact and saves it using the artifact service."""
    print(f"  [Tool] Creating artifact '{filename}' with content: '{content_text}'")
    # A Part can be created from text, bytes, or a Blob
    artifact_part = Part(text=content_text) # Or Part(inline_data=Blob(mime_type="text/plain", data=content_text.encode()))

    version = await tool_context.save_artifact(filename=filename, artifact=artifact_part)
    return {"filename_saved": filename, "version": version, "status": "success"}

save_tool = FunctionTool(func=create_and_save_text_artifact)

# Tool to load an artifact
async def load_text_artifact_content(filename: str, tool_context: ToolContext) -> dict:
    """Loads a text artifact and returns its content."""
    print(f"  [Tool] Attempting to load artifact '{filename}'...")
    artifact_part = await tool_context.load_artifact(filename=filename) # Loads latest version by default
    if artifact_part and artifact_part.text:
        return {"filename_loaded": filename, "content": artifact_part.text, "status": "success"}
    elif artifact_part and artifact_part.inline_data: # If saved as bytes
        return {"filename_loaded": filename, "content": artifact_part.inline_data.data.decode(), "status": "success"}
    return {"filename_loaded": filename, "error": "Artifact not found or not text.", "status": "failure"}

load_tool = FunctionTool(func=load_text_artifact_content)

artifact_agent = Agent(
    name="artifact_handler_agent",
    model="gemini-2.0-flash",
    instruction="You can create text files (artifacts) and later read them. "
                "Use 'create_and_save_text_artifact' to save content. "
                "Use 'load_text_artifact_content' to read content from a previously saved file.",
    tools=[save_tool, load_tool]
)

if __name__ == "__main__":
    # InMemoryRunner uses InMemoryArtifactService by default
    runner = InMemoryRunner(agent=artifact_agent, app_name="InMemoryArtifactApp")
    session_id = "s_artifact_mem"
    user_id = "mem_artifact_user"
    create_session(runner, user_id=user_id, session_id=session_id)  # Create a session for the user

    async def main():
        # Turn 1: Create an artifact
        prompt1 = "Please create a file named 'notes.txt' with the content 'ADK is great for building agents.'"
        print(f"\\n--- Turn 1 --- \\nYOU: {prompt1}")
        user_message1 = Content(parts=[Part(text=prompt1)], role="user")  # User message to the agent
        print("AGENT: ", end="", flush=True)
        async for event in runner.run_async(user_id="mem_artifact_user", session_id=session_id, new_message=user_message1):
            if event.content and event.content.parts[0].text and not event.get_function_calls():
                print(event.content.parts[0].text.strip())

        # Verify artifact was saved (InMemoryArtifactService specific inspection)
        # In a real app, the agent would confirm or you'd check via another tool/Dev UI.
        saved_artifacts = await runner.artifact_service.list_artifact_keys(
            app_name="InMemoryArtifactApp", user_id="mem_artifact_user", session_id=session_id
        )
        print(f"  [DEBUG] Artifacts in session '{session_id}': {saved_artifacts}")
        assert "notes.txt" in saved_artifacts

        # Turn 2: Load the artifact
        prompt2 = "Now, please read the content of 'notes.txt'."
        print(f"\\n--- Turn 2 --- \\nYOU: {prompt2}")
        user_message2 = Content(parts=[Part(text=prompt2)], role="user")  # User message to the agent
        print("AGENT: ", end="", flush=True)
        async for event in runner.run_async(user_id="mem_artifact_user", session_id=session_id, new_message=user_message2):
            if event.content and event.content.parts[0].text and not event.get_function_calls():
                print(event.content.parts[0].text.strip())

    asyncio.run(main())
