# artifacts_examples/load_artifacts_tool_demo.py
from google.adk.agents import Agent
from google.adk.tools import load_artifacts
from google.adk.tools import FunctionTool, ToolContext 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part, Blob
import asyncio

from ...utils import load_environment_variables, create_session
load_environment_variables()  # Load environment variables for ADK configuration

# Tool to create and save an artifact (same as before)
async def create_image_artifact(filename: str, tool_context: ToolContext) -> dict:
    """Creates a dummy PNG image artifact."""
    print(f"  [Tool] Creating dummy image artifact '{filename}'")
    # Dummy PNG (1x1 transparent pixel)
    dummy_png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    artifact_part = Part(inline_data=Blob(mime_type="image/png", data=dummy_png_data))
    version = await tool_context.save_artifact(filename=filename, artifact=artifact_part)
    return {"filename_saved": filename, "version": version, "status": "success"}

save_image_tool = FunctionTool(func=create_image_artifact)

# Agent using LoadArtifactsTool
artifact_viewer_agent = Agent(
    name="artifact_viewer",
    model="gemini-2.0-flash", 
    instruction="You can create image artifacts and later view them. "
                "If artifacts are listed as available, and the user asks about one, "
                "use the 'load_artifacts' function to get its content before describing it.",
    tools=[save_image_tool, load_artifacts] # Add load_artifacts_tool
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=artifact_viewer_agent, app_name="ArtifactViewerApp")
    session_id = "s_artifact_viewer"
    user_id = "viewer_user"
    create_session(runner, user_id=user_id, session_id=session_id)  # Create a session for the user

    async def main():
        # Turn 1: Create an image artifact
        prompt1 = "Please create a dummy image named 'logo.png'."
        print(f"\\n--- Turn 1: Create Artifact --- \\nYOU: {prompt1}")
        user_message1 = Content(parts=[Part(text=prompt1)], role="user")  # User message to the agent
        print("AGENT: ", end="", flush=True)
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message1):
            if event.content and event.content.parts[0].text and not event.get_function_calls():
                print(event.content.parts[0].text.strip())

        # Turn 2: Ask about the artifact. `load_artifacts_tool` will inform the LLM it exists.
        # LLM should then call `load_artifacts`.
        prompt2 = "Describe the 'logo.png' artifact you created."
        print(f"\\n--- Turn 2: Ask to Describe Artifact --- \\nYOU: {prompt2}")
        user_message2 = Content(parts=[Part(text=prompt2)], role="user")  # User message to the agent
        print("AGENT: ", end="", flush=True)
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message2):
            # For CLI, we'll just see the final answer.
            # Dev UI Trace would show:
            # - Sys Instruction: "Artifacts available: ['logo.png']..."
            # - LLM calls: load_artifacts(artifact_names=['logo.png'])
            # - Event: Tool response from load_artifacts (just echoes names)
            # - Next LLM call's history includes: User: Artifact logo.png is: <Part with inline_data>
            # - LLM final response: "The artifact 'logo.png' is an image file..."
            if event.content and event.content.parts[0].text and not event.get_function_calls():
                print(event.content.parts[0].text.strip())

        # Check the artifact service to see the "logo.png"
        # loaded_artifact_part = await runner.artifact_service.load_artifact("ArtifactViewerApp", "viewer_user", session_id, "logo.png")
        # assert loaded_artifact_part is not None
        # assert loaded_artifact_part.inline_data.mime_type == "image/png"

    asyncio.run(main())
