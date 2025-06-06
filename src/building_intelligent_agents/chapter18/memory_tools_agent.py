# memory_examples/memory_tools_agent.py
from google.adk.agents import Agent
from google.adk.tools import load_memory, preload_memory
from google.adk.runners import InMemoryRunner
from google.adk.sessions.session import Session
from google.adk.events.event import Event
from google.adk.memory import InMemoryMemoryService
from google.genai.types import Content, Part
import time
import asyncio

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM, DEFAULT_REASONING_LLM
load_environment_variables()  # Load environment variables for ADK configuration

# Setup dummy memory as in the InMemoryMemoryService example
memory_service_instance = InMemoryMemoryService()
past_events_for_memory = [
    Event(author="user", timestamp=time.time()-7200, content=Content(parts=[Part(text="I'm planning a trip to Japan next year.")])),
    Event(author="planner_bot", timestamp=time.time()-7190, content=Content(parts=[Part(text="Okay, Japan trip noted for next year!")])),
    Event(author="user", timestamp=time.time()-3600, content=Content(parts=[Part(text="For my Japan trip, I'm interested in Kyoto.")])),
    Event(author="planner_bot", timestamp=time.time()-3590, content=Content(parts=[Part(text="Kyoto is a great choice for your Japan trip!")])),
]
memory_service_instance._session_events["MemoryToolsApp/mem_tools_user"] = {"past_trip_planning": past_events_for_memory}

# Agent using both preload and allowing explicit load
smart_planner_agent = Agent(
    name="smart_trip_planner",
    model=DEFAULT_REASONING_LLM, # Needs good reasoning
    instruction="You are a trip planning assistant. Past conversation snippets might be provided under <PAST_CONVERSATIONS> to help you. "
                "If you need more specific details from past conversations not automatically provided, use the 'load_memory' tool with a targeted query. "
                "Remember to be helpful and use retrieved information effectively.",
    tools=[
        preload_memory, # Will automatically add relevant context to system instruction
        load_memory     # Allows LLM to explicitly query memory
    ]
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=smart_planner_agent, app_name="MemoryToolsApp")
    runner.memory_service = memory_service_instance # Inject our populated memory service

    user_id = "mem_tools_user"
    session_id = "current_trip_planning"
    create_session(runner, user_id=user_id, session_id=session_id)  # Create a session for the user

    async def run_planner_turn(prompt_text):
        print(f"\nYOU: {prompt_text}")
        user_message = Content(parts=[Part(text=prompt_text)], role="user")  # User message to the agent
        print("SMART_TRIP_PLANNER: ", end="", flush=True)

        # The Dev UI Trace is invaluable here to see:
        # 1. What `preload_memory_tool` adds to the system instruction.
        # 2. If/when `load_memory_tool` is called by the LLM.
        # 3. The results of `load_memory_tool`.
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text and not (hasattr(part, 'thought') and part.thought): # Don't print thoughts for cleaner CLI
                        print(part.text, end="", flush=True)
                    elif part.function_call:
                        print(f"\n  [TOOL CALL by {event.author}]: {part.function_call.name}({part.function_call.args})", end="")
                    # We might not see tool responses directly if preload_memory_tool is effective
                    # or if load_memory_tool's output is summarized by LLM.
        print()

    async def main():
        # Query that should benefit from preload_memory_tool
        await run_planner_turn("I mentioned a country I want to visit. What was it and which city was I interested in there?")
        # Expected: PreloadMemoryTool finds "Japan" and "Kyoto". Agent answers directly.

        # Query that might require explicit load_memory if preload isn't specific enough
        # (or if we wanted to demonstrate explicit call)
        # await run_planner_turn("What were the exact first two things I told you about my trip planning?")
        # Expected (if LLM decides to use load_memory): LLM calls load_memory(query="first two things about trip planning")

    asyncio.run(main())
