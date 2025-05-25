
# flows_planners_examples/research_assistant_planner.py
from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner
from google.adk.tools import google_search 
from google.adk.tools import FunctionTool
from google.adk.tools.load_web_page import load_web_page 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio
web_page_loader_tool = FunctionTool(func=load_web_page); research_planner = PlanReActPlanner()
research_assistant = Agent(
    name="research_assistant_planner", model="gemini-1.5-pro-latest", 
    instruction="Research assistant. Plan task. Use search for info/URLs. Use load_web_page for URL content. Synthesize comprehensive answer. Follow Plan-Reason-Act-Observe.",
    tools=[google_search, web_page_loader_tool], planner=research_planner
)
if __name__ == "__main__":
    runner = InMemoryRunner(agent=research_assistant, app_name="ResearchPlannerApp")
    prompt = "Main challenges and opportunities in quantum computing today?"
    print(f"YOU: {prompt}"); user_message = Content(parts=[Part(text=prompt)])
    print("RESEARCH_ASSISTANT (Follow trace in Dev UI for full ReAct flow):\n")
    async def main():
        printed_thoughts = set(); full_final_answer_parts = []
        async for event in runner.run_async(user_id="research_user", session_id="s_research_plan", new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    is_thought = hasattr(part, 'thought') and part.thought
                    if part.text and not is_thought: print(part.text, end=""); full_final_answer_parts.append(part.text)
                    elif part.text and is_thought: 
                        thought_text = part.text.strip()
                        if thought_text not in printed_thoughts: print(f"\n  [THOUGHT/PLAN]:\n  {thought_text}\n  ", end=""); printed_thoughts.add(thought_text)
                    elif part.function_call : print(f"\n  [TOOL CALL]: {part.function_call.name}({part.function_call.args})\n  ", end="")
                    elif part.function_response: print(f"\n  [TOOL RESPONSE for {part.function_response.name}]: (Content might be long)\n  ", end="")
        print("\n\n--- Research Assistant's Combined Final Answer ---"); print("".join(full_final_answer_parts).strip())
    asyncio.run(main())

