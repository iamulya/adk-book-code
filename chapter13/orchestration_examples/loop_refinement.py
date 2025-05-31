# orchestration_examples/loop_refinement.py
from google.adk.agents import Agent, LoopAgent # Import LoopAgent
from google.adk.tools import FunctionTool, ToolContext, exit_loop # Import exit_loop
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio

from ...utils import load_environment_variables, create_session
load_environment_variables()

# --- Define Sub-Agent for the Loop ---
# This agent will try to "refine" a draft.
# In a real scenario, it might get feedback from another agent or the user.

def check_draft_quality(draft: str, tool_context: ToolContext) -> dict:
    """Simulates checking draft quality. Exits loop if 'final' is in draft."""
    iteration = tool_context.state.get("loop_iteration", 0) + 1
    tool_context.state["loop_iteration"] = iteration
    tool_context.state["current_draft"] = draft  # Update the current draft in state

    if "final" in draft.lower() or iteration >= 3: # Exit condition
        print(f"    [QualityCheckTool] Draft meets criteria or max iterations ({iteration}) reached. Signaling exit.")
        exit_loop(tool_context) # Call the exit_loop tool
        return {"quality": "good", "feedback": "Looks good!" if "final" in draft.lower() else "Max iterations reached.", "action": "exit"}
    else:
        print(f"    [QualityCheckTool] Draft needs more work (iteration {iteration}).")
        return {"quality": "poor", "feedback": "Needs more detail about ADK benefits.", "action": "refine"}

quality_check_tool = FunctionTool(func=check_draft_quality)

# The sub-agent that does the work and decides to exit
drafting_agent = Agent(
    name="draft_refiner",
    model="gemini-2.0-flash",
    instruction="You are a document drafter. You will be given a topic and previous draft (if any, from `state['current_draft']`). "
                "Generate or refine the draft. Then, use the 'check_draft_quality' tool to assess it. "
                "The tool will provide feedback. If the tool signals to exit, your job is done for this iteration. "
                "If it signals to refine, use the feedback to improve the draft in your next thought process.",
    description="Drafts and refines documents iteratively.",
    tools=[quality_check_tool]
)

# --- Define the LoopAgent ---
iterative_refinement_loop = LoopAgent(
    name="document_refinement_loop",
    description="Iteratively refines a document until quality criteria are met.",
    sub_agents=[drafting_agent],
    max_iterations=5 # A safeguard, the tool will exit sooner
)

# --- Running the LoopAgent ---
if __name__ == "__main__":
    runner = InMemoryRunner(agent=iterative_refinement_loop, app_name="LoopRefineApp")
    session_id = "s_loop_refine"
    user_id = "loop_user"

    initial_prompt = "Draft a short paragraph about the benefits of ADK. Initial draft: 'ADK is a toolkit.'"
    print(f"YOU: {initial_prompt}")
    user_message = Content(parts=[Part(text=initial_prompt)], role="user")  # User message to the agent

    # Initialize state for the first draft
    initial_state = {"current_draft": "ADK is a toolkit."}
    create_session(runner, user_id=user_id, session_id=session_id, state=initial_state.copy())

    async def main():
        final_agent_responses = []
        # LoopAgent yields events from its sub_agents.
        # The `escalate` action from `exit_loop` will stop the LoopAgent.
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
            # For LoopAgent, it's often useful to pass initial state for the loop
            # We can modify the runner to set this, or have an outer orchestrator.
            # For simplicity, let's assume drafting_agent is smart enough or has it in context.
            # A better way for LoopAgent might be an initial context-setting agent before the loop.
            # For this example, we'll have the drafting_agent look for 'current_draft' in state.
        ):
            current_session = await runner.session_service.get_session(
                app_name="LoopRefineApp", user_id=user_id, session_id=session_id
            )
            print(f"  EVENT from [{event.author}] (Loop Iteration {current_session.state.get('loop_iteration', 0)}):") # HACK: Peeking into state
            if event.actions and event.actions.escalate:
                print("    ESCALATE signal received. Loop will terminate.")

            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        print(f"    Tool Call: {part.function_call.name}({part.function_call.args})")
                    elif part.function_response:
                        print(f"    Tool Response for {part.function_response.name}: {part.function_response.response}")

        print("\\n--- Final Output from Loop (last substantive text from sub-agent) ---")

        print(f"\nFinal session state: {current_session.state}")

    asyncio.run(main())