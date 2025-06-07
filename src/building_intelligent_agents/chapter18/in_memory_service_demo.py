from google.adk.agents import Agent
from google.adk.tools import FunctionTool, ToolContext # For saving to memory & searching
from google.adk.runners import InMemoryRunner
from google.adk.sessions.session import Session
from google.adk.events.event import Event
from google.adk.memory import InMemoryMemoryService # Explicit import for clarity
from google.genai.types import Content, Part
import time
import asyncio

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()  # Load environment variables for ADK configuration

# --- Agent and Tools ---
async def save_current_session_to_long_term_memory(tool_context: ToolContext) -> str:
    """Explicitly saves the current session's events to long-term memory."""
    if not tool_context._invocation_context.memory_service:
        return "Error: Memory service is not available."

    # Get the full current session object from the context
    current_session = tool_context._invocation_context.session
    await tool_context._invocation_context.memory_service.add_session_to_memory(current_session)
    return f"Session {current_session.id} has been committed to long-term memory."

save_to_memory_tool = FunctionTool(save_current_session_to_long_term_memory)

async def recall_information(query: str, tool_context: ToolContext) -> dict:
    """Searches long-term memory for information related to the query."""
    if not tool_context._invocation_context.memory_service:
        return {"error": "Memory service is not available."}

    search_response = await tool_context.search_memory(query)

    if not search_response.memories:
        return {"found_memories": 0, "results": "No relevant memories found."}

    # For InMemoryMemoryService, results are raw MemoryEntry objects. Let's format them.
    formatted_results = []
    for mem_entry in search_response.memories[:3]: # Limit for brevity
        text_parts = [p.text for p in mem_entry.content.parts if p.text]
        formatted_results.append(
            f"Author: {mem_entry.author}, Timestamp: {mem_entry.timestamp}, Content: {' '.join(text_parts)}"
        )
    return {"found_memories": len(search_response.memories), "results": formatted_results}

recall_tool = FunctionTool(recall_information)

memory_interactive_agent = Agent(
    name="memory_keeper",
    model=DEFAULT_LLM,
    instruction=(
        "You have access to a shared, long-term memory that persists across our conversations (sessions). "
        "Use 'save_current_session_to_long_term_memory' to save important facts. "
        "When asked to recall information, especially if it seems like something discussed previously (even in a different session), "
        "use 'recall_information' with a relevant search query to check this long-term memory."
    ),
    tools=[save_to_memory_tool, recall_tool]
)

if __name__ == "__main__":
    # Explicitly create an InMemoryMemoryService instance to interact with
    memory_service = InMemoryMemoryService()

    # Initialize runner with our specific memory_service
    runner = InMemoryRunner(agent=memory_interactive_agent, app_name="MemoryDemoApp")
    runner.memory_service = memory_service # Override the default one from InMemoryRunner

    user_id = "user_mem_test"
    session_id_1 = "memory_session_1"
    session_id_2 = "memory_session_2"
    create_session(runner, user_id=user_id, session_id=session_id_1)  # Create first session
    create_session(runner, user_id=user_id, session_id=session_id_2)  # Create second session

    async def run_turn(uid, sid, prompt_text, expected_tool_call=None):
        print(f"\n--- Running for User: {uid}, Session: {sid} ---")
        print(f"YOU: {prompt_text}")
        user_message = Content(parts=[Part(text=prompt_text)], role="user")
        print("AGENT: ", end="", flush=True)
        async for event in runner.run_async(user_id=uid, session_id=sid, new_message=user_message):
            if event.author == memory_interactive_agent.name and event.content and event.content.parts and not event.get_function_calls() and not event.get_function_responses(): 
                print(event.content.parts[0].text.strip())
            # For debugging, show tool calls
            if event.get_function_calls():
                for fc in event.get_function_calls():
                    print(f"\n  [TOOL CALL by {event.author}]: {fc.name}({fc.args})")
                    if expected_tool_call and fc.name == expected_tool_call:
                        print(f"    (Matches expected tool call: {expected_tool_call})")
            if event.get_function_responses():
                 for fr in event.get_function_responses():
                    print(f"\n  [TOOL RESPONSE to {fr.name}]: {fr.response}")

    async def main():
        # Turn 1 (Session 1): Store some information
        await run_turn(user_id, session_id_1, "Please remember that my favorite hobby is hiking and save this session.",
                       expected_tool_call="save_current_session_to_long_term_memory")

        # Turn 2 (Session 1): Recall information
        await run_turn(user_id, session_id_1, "What did I tell you about my favorite hobby?",
                       expected_tool_call="recall_information")

        # Turn 3 (New Session - Session 2): Try to recall information from Session 1
        await run_turn(user_id, session_id_2, "Do you remember my favorite hobby?",
                       expected_tool_call="recall_information")

        # Verify memory content (InMemoryMemoryService specific inspection)
        search_res = await memory_service.search_memory(app_name="MemoryDemoApp", user_id=user_id, query="hobby")
        print(f"\n[DEBUG] Direct memory search for 'hobby' found {len(search_res.memories)} entries.")
        for entry in search_res.memories:
            print(f"  - Author: {entry.author}, Content: {entry.content.parts[0].text if entry.content.parts else ''}")

    asyncio.run(main())