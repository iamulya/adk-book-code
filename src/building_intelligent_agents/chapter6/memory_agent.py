# tools_examples/memory_agent.py
from google.adk.agents import Agent
from google.adk.tools import load_memory, preload_memory
from google.adk.runners import InMemoryRunner
from google.adk.sessions.session import Session
from google.adk.events.event import Event
from google.genai.types import Content, Part
import time

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM

load_environment_variables()

# --- Setup a MemoryService with some data ---
# In a real app, this would be a persistent service like VertexAiRagMemoryService
# For this example, we'll manually populate the InMemoryMemoryService.
memory_service_instance = InMemoryRunner(agent=Agent(name="dummy"), app_name="MemApp").memory_service

# Create a dummy past session to populate memory
past_session = Session(
    app_name="MemApp",
    user_id="memory_user",
    id="past_session_abc",
    events=[
        Event(author="user", timestamp=time.time()-3600, content=Content(parts=[Part(text="My favorite color is blue.")])),
        Event(author="mem_agent", timestamp=time.time()-3590, content=Content(parts=[Part(text="Okay, I'll remember that your favorite color is blue.")])),
        Event(author="user", timestamp=time.time()-1800, content=Content(parts=[Part(text="I live in Paris.")])),
        Event(author="mem_agent", timestamp=time.time()-1790, content=Content(parts=[Part(text="Noted, you live in Paris.")])),
    ]
)
# await memory_service_instance.add_session_to_memory(past_session) # Call in async context if not using InMemory

# For InMemoryMemoryService, direct manipulation for setup:
memory_service_instance._session_events[f"MemApp/memory_user"] = {"past_session_abc": past_session.events}


# --- Agent using PreloadMemoryTool ---
proactive_memory_agent = Agent(
    name="proactive_memory_agent",
    model=DEFAULT_LLM,
    instruction="You are a helpful assistant that remembers things about the user. Relevant past conversations will be provided to you automatically.",
    tools=[preload_memory] # Just add it, it works automatically
)

# --- Agent using LoadMemoryTool ---
reactive_memory_agent = Agent(
    name="reactive_memory_agent",
    model=DEFAULT_LLM,
    instruction="You are a helpful assistant. If you need to recall past information to answer a question, use the 'load_memory' tool with a relevant query.",
    tools=[load_memory]
)

root_agent = reactive_memory_agent

if __name__ == "__main__":
    print("--- Testing Proactive Memory Agent (with PreloadMemoryTool) ---")
    # The InMemoryRunner for proactive_memory_agent needs our populated memory_service_instance
    runner_proactive = InMemoryRunner(agent=proactive_memory_agent, app_name="MemApp")
    runner_proactive.memory_service = memory_service_instance # Inject our populated memory service

    session_id = "s_proactive"
    user_id = "memory_user"
    create_session(runner_proactive, session_id=session_id, user_id=user_id)

    prompt1 = "What do you know about me?"
    print(f"YOU: {prompt1}")
    user_message1 = Content(parts=[Part(text=prompt1)], role="user")
    print("PROACTIVE_AGENT: ", end="", flush=True)
    for event in runner_proactive.run(user_id=user_id, session_id=session_id, new_message=user_message1):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: print(part.text, end="")
    print()

    print("\\n--- Testing Reactive Memory Agent (with LoadMemoryTool) ---")
    runner_reactive = InMemoryRunner(agent=reactive_memory_agent, app_name="MemApp")
    runner_reactive.memory_service = memory_service_instance # Inject our populated memory service

    reactive_session_id = "s_reactive"
    create_session(runner_reactive, session_id=reactive_session_id, user_id=user_id)

    prompt2 = "Remind me of my favorite color."
    print(f"YOU: {prompt2}")
    user_message2 = Content(parts=[Part(text=prompt2)], role="user")
    print("REACTIVE_AGENT: ", end="", flush=True)
    for event in runner_reactive.run(user_id=user_id, session_id=reactive_session_id, new_message=user_message2):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: print(part.text, end="")
    print()


