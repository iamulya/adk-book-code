from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner # Key import
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.adk.sessions.state import State # For state manipulation
from google.adk.agents.callback_context import CallbackContext # For planner state
from google.genai.types import Content, Part

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_REASONING_LLM
load_environment_variables()

# Dummy tools for demonstration
def search_knowledge_base(query: str, tool_context: CallbackContext) -> str:
    """Searches the company knowledge base for a query."""
    tool_context.state[State.TEMP_PREFIX + "last_search_query"] = query # Example of using temp state
    if "policy" in query.lower():
        return "Found document: 'HR001: Work From Home Policy - Employees can work remotely twice a week with manager approval.'"
    if "onboarding" in query.lower():
        return "Found document: 'IT005: New Employee Onboarding Checklist - Includes setting up accounts and mandatory training.'"
    return "No relevant documents found for your query."

def request_manager_approval(employee_id: str, reason: str) -> str:
    """Sends a request to the employee's manager for approval."""
    return f"Approval request sent for employee {employee_id} regarding: {reason}. Status: PENDING."

search_tool = FunctionTool(func=search_knowledge_base)
approval_tool = FunctionTool(func=request_manager_approval)

# Create the PlanReActPlanner
react_planner = PlanReActPlanner()

# Create the agent
hr_assistant_react = Agent(
    name="hr_assistant_react",
    model=DEFAULT_REASONING_LLM, # Needs a strong reasoning model
    instruction="You are an HR assistant. Follow the Plan-Reason-Act-Observe cycle. First, create a plan. Then, for each step, provide reasoning, take an action (use a tool if necessary), and then reason about the observation to proceed or replan. Conclude with a final answer.",
    tools=[search_tool, approval_tool],
    planner=react_planner # Assign the planner
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=hr_assistant_react, app_name="ReActHrApp")
    session_id = "s_react"
    user_id = "hr_user"
    create_session(runner, user_id=user_id, session_id=session_id)

    # This prompt requires multiple steps and decisions
    prompt = "Employee emp456 wants to work from home full-time. What's the process?"

    print(f"YOU: {prompt}")
    user_message = Content(parts=[Part(text=prompt)], role="user")  # User message to the agent
    print("HR_ASSISTANT_REACT (Follow trace in Dev UI for full ReAct flow):\n")

    full_response_parts = []
    async def main():
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
            # The ReAct planner often produces "thought" parts that are not meant for direct display.
            # The final answer is typically marked or is the last textual part after planning/actions.
            # For this CLI example, we'll just print all non-thought text.
            # In the Dev UI, thoughts are clearly distinguished in the Trace.
            if event.content and event.content.parts:
                for part in event.content.parts:
                    is_thought = hasattr(part, 'thought') and part.thought
                    if part.text and not is_thought:
                        print(part.text, end="")
                        full_response_parts.append(part.text)
                    elif part.text and is_thought: # Optionally print thoughts for CLI demo
                        print(f"\n  [THOUGHT/PLAN]:\n  {part.text.strip()}\n  ", end="")
                    elif part.function_call :
                         print(f"\n  [TOOL CALL]: {part.function_call.name}({part.function_call.args})\n  ", end="")
                    elif part.function_response:
                         print(f"\n  [TOOL RESPONSE to {part.function_response.name}]: {part.function_response.response}\n  ", end="")
        print("\n--- Combined Agent Response ---")
        print("".join(full_response_parts))

    import asyncio
    asyncio.run(main())