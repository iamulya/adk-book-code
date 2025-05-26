
# orchestration_examples/loop_refinement.py
from google.adk.agents import Agent, LoopAgent 
from google.adk.tools import FunctionTool, ToolContext, exit_loop 
from google.adk.runners import InMemoryRunner; from google.genai.types import Content, Part; import asyncio; from google.adk.sessions.state import State
def check_draft_quality(draft: str, tool_context: ToolContext) -> dict:
    """Simulates checking draft. Exits if 'final' in draft or 3 iterations."""
    iteration=tool_context.state.get(State.TEMP_PREFIX+"loop_iteration",0)+1; tool_context.state[State.TEMP_PREFIX+"loop_iteration"]=iteration
    if "final" in draft.lower() or iteration >=3:
        print(f"    [QualityCheckTool] Criteria met/max iterations ({iteration}). Signaling exit.")
        exit_loop(tool_context); return {"quality":"good","feedback":"Looks good!" if "final" in draft.lower() else "Max iterations.","action":"exit"}
    else: print(f"    [QualityCheckTool] Needs work (iter {iteration})."); return {"quality":"poor","feedback":"Needs more detail.","action":"refine"}
quality_check_tool=FunctionTool(check_draft_quality)
drafting_agent=Agent(name="draft_refiner",model="gemini-2.0-flash",instruction="Draft/refine doc based on `state['current_draft']`. Use 'check_draft_quality' tool. If tool says refine, use feedback.",tools=[quality_check_tool])
iterative_refinement_loop=LoopAgent(name="doc_refinement_loop",sub_agents=[drafting_agent],max_iterations=5)
if __name__=="__main__":
    runner=InMemoryRunner(agent=iterative_refinement_loop,app_name="LoopRefineApp")
    initial_prompt="Draft short paragraph on ADK benefits. Initial: 'ADK is a toolkit.'"
    print(f"YOU: {initial_prompt}");user_message=Content(parts=[Part(text=initial_prompt)]);initial_state={"current_draft":"ADK is a toolkit."}
    async def main():
        final_agent_responses=[]
        s_id="s_loop_ref"; u_id="loop_user"; app_n="LoopRefineApp"
        # Initialize session state for the LoopAgent example more cleanly
        await runner.session_service.create_session(app_name=app_n, user_id=u_id, session_id=s_id, state=initial_state.copy())
        async for event in runner.run_async(user_id=u_id,session_id=s_id,new_message=user_message):
            current_iter = (await runner.session_service.get_session(app_n, u_id, s_id)).state.get(State.TEMP_PREFIX+"loop_iteration",0)
            print(f"  EVENT from [{event.author}] (Loop Iter {current_iter}):")
            if event.actions and event.actions.escalate: print("    ESCALATE received. Loop will terminate.")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text: print(f"    Text: {part.text.strip()}"); 
                    # Update current_draft in state for next iteration by drafting_agent
                    if event.author == drafting_agent.name and not (event.get_function_calls() or event.get_function_responses()):
                         current_s = await runner.session_service.get_session(app_n, u_id, s_id)
                         current_s.state["current_draft"] = part.text.strip() # This updates in-memory version.
                                                                               # For DB, event.actions.state_delta in agent would be better.
                         final_agent_responses.append(part.text.strip())

                    elif part.function_call: print(f"    Tool Call: {part.function_call.name}({part.function_call.args})")
                    elif part.function_response: print(f"    Tool Resp for {part.function_response.name}: {part.function_response.response}")
        print("\n--- Final Output from Loop ---"); print("LOOP_OUT: "+ (final_agent_responses[-1] if final_agent_responses else "N/A"))
        s=await runner.session_service.get_session(app_n,u_id,s_id); print(f"\nFinal state: {s.state}")
    asyncio.run(main())

