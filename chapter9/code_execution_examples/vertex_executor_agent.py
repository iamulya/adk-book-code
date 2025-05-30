from google.adk.agents import Agent
# Ensure google-cloud-aiplatform is installed sufficiently
try:
    from google.adk.code_executors import VertexAiCodeExecutor # Key import
    VERTEX_SDK_AVAILABLE = True
except ImportError:
    print("Vertex AI SDK (with preview features for extensions) not found. Please ensure 'google-cloud-aiplatform' is installed and up to date.")
    VERTEX_SDK_AVAILABLE = False

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os
from ...utils import load_environment_variables, create_session
load_environment_variables()

vertex_agent = None
if VERTEX_SDK_AVAILABLE:
    # Ensure GOOGLE_CLOUD_PROJECT is set in your environment
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("Error: GOOGLE_CLOUD_PROJECT environment variable must be set for VertexAiCodeExecutor.")
    else:
        try:
            print("Initializing VertexAiCodeExecutor...")
            # You can optionally provide a resource_name for an existing Code Interpreter Extension instance
            # vertex_executor = VertexAiCodeExecutor(resource_name="projects/.../locations/.../extensions/...")
            vertex_executor = VertexAiCodeExecutor() # Will create or use an existing one based on env var or default
            print(f"VertexAiCodeExecutor initialized. Using extension: {vertex_executor._code_interpreter_extension.gca_resource.name}")


            vertex_agent = Agent(
                name="vertex_code_agent",
                model="gemini-2.0-flash",
                instruction="You are an advanced AI assistant. Write Python code to perform calculations or data tasks. Your code will be executed in a secure Vertex AI environment. Default libraries like pandas, numpy, matplotlib are available.",
                code_executor=vertex_executor
            )
        except Exception as e:
            print(f"Failed to initialize VertexAiCodeExecutor. Ensure Vertex AI API is enabled and auth is correct. Error: {e}")
else:
    print("Skipping VertexAiCodeExecutor example as Vertex AI SDK is not available/configured.")


if __name__ == "__main__":
    if not vertex_agent:
        print("Vertex Agent not initialized. Exiting.")
    else:
        runner = InMemoryRunner(agent=vertex_agent, app_name="VertexCodeApp")
        session_id = "s_vertex"
        user_id = "vertex_user"
        create_session(runner, user_id=user_id, session_id=session_id)

        prompts = [
            "Plot a simple sine wave using matplotlib and save it as 'sine_wave.png'. Describe the plot.",
            "Create a pandas DataFrame with columns 'City' and 'Population' for three cities, then print the average population."
        ]
        # ... (runner and async main loop as in UnsafeLocalCodeExecutor example) ...
        # The Vertex AI Code Interpreter handles file outputs (like 'sine_wave.png')
        # and makes them available in the CodeExecutionResult.
        # ADK can then save these as artifacts.
        print("Vertex AI Code Interpreter agent ready.")
        # Add async main loop here
        async def main():
            for prompt_text in prompts:
                print(f"\\nYOU: {prompt_text}")
                user_message = Content(parts=[Part(text=prompt_text)], role="user")
                print("ASSISTANT (via VertexAiCodeExecutor): ", end="", flush=True)
                # Note: The actual plot image won't be printed to console here.
                # In the Dev UI or a proper app, you'd handle the output_files
                # from the CodeExecutionResult (which are then put into Event.actions.artifact_delta).
                async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text: print(part.text, end="", flush=True)
                print()
                # To see artifacts:
                if runner.artifact_service:
                    artifacts = await runner.artifact_service.list_artifact_keys(
                        app_name="VertexCodeApp", user_id="vertex_user", session_id="s_vertex"
                    )
                    if artifacts:
                        print(f"  (Artifacts created: {artifacts})")
        import asyncio
        asyncio.run(main())
