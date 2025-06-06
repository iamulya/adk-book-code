from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner, RunConfig # Import RunConfig
from google.adk.agents.run_config import StreamingMode # Import StreamingMode
from google.genai.types import Content, Part
import asyncio

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

streaming_demo_agent = Agent(
    name="streaming_writer",
    model=DEFAULT_LLM,
    instruction="Write a very short story (10-15 sentences) about a curious cat."
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=streaming_demo_agent, app_name="StreamingApp")
    session_id = "s_streaming"
    user_id = "streaming_user"
    create_session(runner, user_id=user_id, session_id=session_id)

    user_message = Content(parts=[Part(text="Tell me a story.")], role="user") # Prompt for the agent

    async def run_with_streaming():
        print("Streaming Agent Response:")
        # Configure the runner to use SSE (Server-Sent Events) streaming
        run_config = RunConfig(streaming_mode=StreamingMode.SSE)

        async for event in runner.run_async( # Use run_async for streaming
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
            run_config=run_config # Pass the run_config
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True) # Print chunks as they arrive
        print("\\n--- End of Stream ---")

    asyncio.run(run_with_streaming())