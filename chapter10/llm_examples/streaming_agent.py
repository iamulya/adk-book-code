
# llm_examples/streaming_agent.py
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner, RunConfig 
from google.adk.agents.run_config import StreamingMode 
from google.genai.types import Content, Part
import asyncio
streaming_demo_agent = Agent(name="streaming_writer",model="gemini-2.0-flash",instruction="Write short story (2-3 sentences) about a cat.")
if __name__ == "__main__":
    runner = InMemoryRunner(agent=streaming_demo_agent, app_name="StreamingApp")
    user_message = Content(parts=[Part(text="Tell me a story.")]) 
    async def run_with_streaming():
        print("Streaming Agent Response:")
        run_config = RunConfig(streaming_mode=StreamingMode.SSE)
        async for event in runner.run_async(user_id="stream_user",session_id="s_stream",new_message=user_message,run_config=run_config):
            if event.content and event.content.parts and event.content.parts[0].text:
                print(event.content.parts[0].text, end="", flush=True) 
        print("\n--- End of Stream ---")
    asyncio.run(run_with_streaming())

