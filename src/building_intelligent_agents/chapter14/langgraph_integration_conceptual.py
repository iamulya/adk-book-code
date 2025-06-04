# advanced_mas/langgraph_integration_conceptual.py
# This is a conceptual example. A full, runnable LangGraph example
# can be quite involved and depends on specific LangGraph setup.
# Ensure 'langgraph' and 'langchain_core' are installed: pip install langgraph langchain_core

from google.adk.agents import Agent as AdkAgent
from google.adk.agents.langgraph_agent import LangGraphAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

# --- Conceptual LangGraph Setup (Illustrative) ---
try:
    from typing import TypedDict, Annotated, Sequence
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver # Simple in-memory checkpointer

    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]
        # Add other state variables your graph needs

    # Define a clear flag for tool requests within AIMessage content
    TOOL_REQUEST_FLAG = "[TOOL_REQUEST_FLAG]"

    def llm_node(state: AgentState):
        # Check the type of the last message to decide behavior
        last_message = state['messages'][-1]
        response_content = ""

        if isinstance(last_message, HumanMessage):
            # User's turn
            user_input = last_message.content
            if "tool" in user_input.lower(): # User mentions "tool"
                # LLM decides to call a tool
                response_content = f"Okay, I understand you want to use a tool for '{user_input}'. Requesting the tool. {TOOL_REQUEST_FLAG}"
            else:
                response_content = f"LangGraph responding to user: '{user_input}'"
        elif isinstance(last_message, AIMessage): # This AIMessage is from tool_node (or a previous llm_node turn)
            # LLM processes the tool's output or continues conversation
            # Ensure this response does NOT contain TOOL_REQUEST_FLAG unless a new tool is needed
            ai_input_content = last_message.content
            response_content = f"Processed previous step. Last AI message was: '{ai_input_content}'. Continuing..."
        else: # Should not happen in this simple graph (e.g. SystemMessage is last)
            response_content = "LangGraph: Unsure how to proceed with the current message state."
        
        print(f"DEBUG: llm_node producing: '{response_content}'")
        return {"messages": [AIMessage(content=response_content)]}

    def tool_node(state: AgentState):
        # This node would execute a tool based on LLM's request
        # The AIMessage from tool_node should reflect the tool's output
        tool_output_content = "LangGraph tool_node executed conceptually. Result: Tool_ABC_Data."
        print(f"DEBUG: tool_node producing: '{tool_output_content}'")
        return {"messages": [AIMessage(content=tool_output_content)]}

    def should_call_tool(state: AgentState):
        # Check the last AI message for the specific flag
        if state['messages'] and isinstance(state['messages'][-1], AIMessage):
            last_ai_content = state['messages'][-1].content
            print(f"DEBUG: should_call_tool checking AI content: '{last_ai_content}'")
            if TOOL_REQUEST_FLAG in last_ai_content:
                print("DEBUG: should_call_tool -> routing to tool_executor")
                return "tool_executor"
        print("DEBUG: should_call_tool -> routing to END")
        return END

    # Create a conceptual graph
    builder = StateGraph(AgentState)
    builder.add_node("llm_entry_point", llm_node)
    builder.add_node("tool_executor", tool_node)

    builder.set_entry_point("llm_entry_point")
    builder.add_conditional_edges(
        "llm_entry_point",
        should_call_tool,
        {"tool_executor": "tool_executor", END: END}
    )
    builder.add_edge("tool_executor", "llm_entry_point") # Loop back after tool use

    memory = MemorySaver()
    runnable_graph = builder.compile(checkpointer=memory)
    LANGGRAPH_SETUP_SUCCESS = True
    print("Conceptual LangGraph graph compiled.")

except ImportError:
    print("LangGraph or LangChain components not found. pip install langgraph langchain_core")
    LANGGRAPH_SETUP_SUCCESS = False
    runnable_graph = None
except Exception as e:
    print(f"Error during LangGraph setup: {e}")
    LANGGRAPH_SETUP_SUCCESS = False
    runnable_graph = None

# --- ADK Agent Definition ---
langgraph_adk_agent = None
orchestrator = None
if LANGGRAPH_SETUP_SUCCESS and runnable_graph:
    langgraph_adk_agent = LangGraphAgent(
        name="my_langgraph_powered_agent",
        graph=runnable_graph, # Pass the compiled LangGraph graph
        instruction="This agent is powered by a LangGraph state machine. Interact normally." # ADK-level instruction
    )
    print("LangGraphAgent initialized.")

    orchestrator = AdkAgent(
            name="main_orchestrator",
            model=DEFAULT_LLM, # Orchestrator's own model
            instruction="Delegate all tasks to my_langgraph_powered_agent.",
            sub_agents=[langgraph_adk_agent]
        )

# --- Running the ADK LangGraphAgent ---
if __name__ == "__main__":
    runner = InMemoryRunner(agent=orchestrator, app_name="LangGraphADKApp")
    session_id = "s_langgraph_adk" # ADK session ID for the orchestrator
    user_id = "lg_user"
    create_session(runner, user_id=user_id, session_id=session_id)

    prompts = [
        "Hello LangGraph agent, tell me about yourself.",
        "use the tool.", # To trigger the tool_node path
        "What happened after the tool use?"
    ]

    async def main():
        for i, prompt_text in enumerate(prompts):
            print(f"\\n--- Turn {i+1} ---")
            print(f"YOU: {prompt_text}")
            user_message_adk = Content(parts=[Part(text=prompt_text)], role="user")

            print("ORCHESTRATOR/LANGGRAPH_AGENT: ", end="", flush=True)
            # The orchestrator will likely decide to transfer to langgraph_adk_agent
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id, 
                new_message=user_message_adk
            ):
                for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
            print()

    asyncio.run(main())