
# advanced_mas/langgraph_integration_conceptual.py
from google.adk.agents import Agent as AdkAgent, LangGraphAgent 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio
LANGGRAPH_SETUP_SUCCESS = False; runnable_graph = None
try:
    from typing import TypedDict, Annotated, Sequence
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver 
    class AgentState(TypedDict): messages: Annotated[Sequence[BaseMessage], lambda x,y: x+y]
    def llm_node(state: AgentState): return {"messages": [AIMessage(content=f"LG LLM node: {state['messages'][-1].content}")]}
    def tool_node(state: AgentState): return {"messages": [AIMessage(content="LG tool_node executed.")]}
    builder = StateGraph(AgentState); builder.add_node("llm_entry", llm_node); builder.add_node("tool_exec", tool_node)
    builder.set_entry_point("llm_entry")
    def should_call_tool(state:AgentState): return "tool_exec" if state['messages'][-1].content and "tool" in state['messages'][-1].content.lower() else END
    builder.add_conditional_edges("llm_entry",should_call_tool,{"tool_exec":"tool_exec",END:END}); builder.add_edge("tool_exec","llm_entry")
    runnable_graph = builder.compile(checkpointer=MemorySaver()); LANGGRAPH_SETUP_SUCCESS=True; print("Conceptual LG graph compiled.")
except ImportError: print("LangGraph/LangChain not found.")
except Exception as e: print(f"LG setup error: {e}")
langgraph_adk_agent = None
if LANGGRAPH_SETUP_SUCCESS and runnable_graph:
    langgraph_adk_agent = LangGraphAgent(name="my_lg_agent", graph=runnable_graph, instruction="LangGraph agent.")
    print("LangGraphAgent initialized.")
if __name__ == "__main__":
    if not langgraph_adk_agent: print("LG ADK Agent not initialized.")
    else:
        orchestrator=AdkAgent(name="main_orch",model="gemini-2.0-flash",instruction="Delegate to LG agent.",sub_agents=[langgraph_adk_agent])
        runner=InMemoryRunner(agent=orchestrator,app_name="LangGraphADKApp"); prompts=["Hello LG agent.","Call conceptual tool."]; session_id_lg="lg_s1"
        async def main():
            for i,prompt_text in enumerate(prompts):
                print(f"\n--- Turn {i+1} ---\nYOU: {prompt_text}")
                user_msg=Content(parts=[Part(text=prompt_text)],role="user"); print("ORCH/LG_AGENT: ",end="",flush=True)
                async for event in runner.run_async(user_id="lg_user",session_id=session_id_lg,new_message=user_msg):
                    if event.author==langgraph_adk_agent.name and event.content and event.content.parts and event.content.parts[0].text:
                        print(event.content.parts[0].text, end="")
                print()
        asyncio.run(main())

