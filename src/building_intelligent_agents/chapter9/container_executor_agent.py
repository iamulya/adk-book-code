from google.adk.agents import Agent
# Ensure 'docker' is installed: pip install google-adk[extensions] or pip install docker
try:
    from google.adk.code_executors import ContainerCodeExecutor # Key import
    DOCKER_AVAILABLE = True
except ImportError:
    print("Docker SDK not found. Please install it ('pip install docker') to run this example.")
    DOCKER_AVAILABLE = False

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os
import atexit # To ensure container cleanup

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

container_agent = None
container_executor_instance = None # To manage its lifecycle

if DOCKER_AVAILABLE:
    # Option 1: Use a pre-existing Python image from Docker Hub
    # container_executor_instance = ContainerCodeExecutor(image="python:3.10-slim")

    # Option 2: Build a custom image from a Dockerfile
    # Create a simple Dockerfile in the same directory (e.g., my_python_env/Dockerfile)
    dockerfile_dir = "my_python_env"
    os.makedirs(dockerfile_dir, exist_ok=True)
    with open(os.path.join(dockerfile_dir, "Dockerfile"), "w") as df:
        df.write("FROM python:3.10-slim\n")
        df.write("RUN pip install numpy pandas\n") # Example: add libraries
        df.write("WORKDIR /app\n")
        df.write("COPY . /app\n") # Not strictly needed if only executing ephemeral code

    try:
        print("Initializing ContainerCodeExecutor (may take a moment to build/pull image)...")
        container_executor_instance = ContainerCodeExecutor(
            docker_path=dockerfile_dir # Path to the directory containing the Dockerfile
            # image="my-custom-adk-executor:latest" # If you build and tag it manually first
        )
        print("ContainerCodeExecutor initialized.")

        container_agent = Agent(
            name="container_code_agent",
            model=DEFAULT_LLM,
            instruction="You are an assistant that writes Python code. I will execute your code in a sandboxed Docker container. You can use numpy and pandas.",
            code_executor=container_executor_instance
        )

        # Ensure the container is cleaned up on exit - ADK should do it on its own. Provided here only for reference
        # def cleanup_container():
        #     if container_executor_instance and hasattr(container_executor_instance, "_ContainerCodeExecutor__cleanup_container"):
        #         print("Cleaning up Docker container...")
        #         # Note: __cleanup_container is an internal method, direct call is for example clarity.
        #         # Proper resource management would ideally be handled by making ContainerCodeExecutor
        #         # an async context manager if it holds long-lived resources like a running container.
        #         # For now, ADK's MCPToolset shows a pattern with AsyncExitStack for resource cleanup.
        #         # A simpler direct cleanup call if the executor instance itself manages its container:
        #         if hasattr(container_executor_instance, "_container") and container_executor_instance._container:
        #             try:
        #                 container_executor_instance._container.stop()
        #                 container_executor_instance._container.remove()
        #                 print(f"Container {container_executor_instance._container.id} stopped and removed.")
        #             except Exception as e:
        #                 print(f"Error during manual container cleanup: {e}")

        # atexit.register(cleanup_container)

    except Exception as e:
        print(f"Failed to initialize ContainerCodeExecutor. Is Docker running and configured? Error: {e}")
        container_agent = None # Fallback
else:
    print("Skipping ContainerCodeExecutor example as Docker SDK is not available.")


if __name__ == "__main__":
    if not container_agent:
        print("Container Agent not initialized. Exiting.")
    else:
        runner = InMemoryRunner(agent=container_agent, app_name="ContainerCodeApp")
        session_id = "s_container_code_test"
        user_id = "container_user"
        create_session(runner, session_id, user_id)
        prompts = [
            "Import numpy and create a 3x3 matrix of zeros, then print it.",
            "Use pandas to create a DataFrame with two columns, 'Name' and 'Age', and add one row of data. Print the DataFrame."
        ]
        # ... (runner and async main loop as in UnsafeLocalCodeExecutor example) ...
        # The interaction flow is similar, but execution is inside Docker.
        print("Container agent ready. Note: First execution might be slower due to Docker image layers.")
        # Add the async main loop here if you want to run prompts
        async def main():
            for prompt_text in prompts:
                print(f"\\nYOU: {prompt_text}")
                user_message = Content(parts=[Part(text=prompt_text)], role="user")
                print("ASSISTANT (via ContainerCodeExecutor): ", end="", flush=True)
                async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text: print(part.text, end="", flush=True)
                print()
        import asyncio
        asyncio.run(main())