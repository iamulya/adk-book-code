
# flows_planners_examples/react_planner_agent.py
from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner
from google.adk.tools import FunctionTool, ToolContext 
from google.adk.runners import InMemoryRunner
from google.adk.sessions.state import State 
from google.adk.agents.callback_context import CallbackContext 
from google.genai.types import Content, Part
import os; import asyncio
def search_knowledge_base(query: str, tool_context: CallbackContext) -> str:
    """Searches company knowledge base."""
    tool_context.state[State.TEMP_PREFIX + "last_search_query"] = query 
    if "policy" in query.lower(): return "Found: 'HR001: WFH Policy - Remote twice a week with approval.'"
    if "onboarding" in query.lower(): return "Found: 'IT005: New Employee Onboarding Checklist.'"
    return "No relevant documents found."
def request_manager_approval(employee_id: str, reason: str) -> str:
    """Sends approval request to manager."""
    return f"Approval for {employee_id} ({reason}) sent. Status: PENDING."
search_tool = FunctionTool(func=search_knowledge_base); approval_tool = FunctionTool(func=request_manager_approval)
react_planner = PlanReActPlanner()
hr_assistant_react = Agent(
    name="hr_assistant_react", model="gemini-1.5-pro-latest", 
    instruction="You are HR assistant. Follow Plan-Reason-Act-Observe. Plan, then reason, then action (tool), then reason on observation. Conclude with final answer.",
    tools=[search_tool, approval_tool], planner=react_planner
)
if __name__ == "__main__":
    runner = InMemoryRunner(agent=hr_assistant_react, app_name="ReActHrApp")
    prompt = "Employee emp456 wants full-time WFH. Process?"
    print(f"YOU: {prompt}"); user_message = Content(parts=[Part(text=prompt)])
    print("HR_ASSISTANT_REACT (Follow trace in Dev UI for full ReAct flow):\n")
    full_response_parts = []
    async def main():
        async for event in runner.run_async(user_id="hr_user", session_id="s_react", new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    is_thought = hasattr(part, 'thought') and part.thought
                    if part.text and not is_thought: print(part.text, end=""); full_response_parts.append(part.text)
                    elif part.text and is_thought: print(f"\n  [THOUGHT/PLAN]:\n  {part.text.strip()}\n  ", end="")
                    elif part.function_call : print(f"\n  [TOOL CALL]: {part.function_call.name}({part.function_call.args})\n  ", end="")
                    elif part.function_response: print(f"\n  [TOOL RESPONSE to {part.function_response.name}]: {part.function_response.response}\n  ", end="")
        print("\n\n--- Combined Agent Response ---"); print("".join(full_response_parts).strip())
    asyncio.run(main())

