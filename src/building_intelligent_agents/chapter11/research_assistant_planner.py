from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search # Using built-in search
from google.adk.tools import FunctionTool
from google.adk.tools.load_web_page import load_web_page 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_REASONING_LLM, DEFAULT_LLM
load_environment_variables()

web_page_loader_tool = FunctionTool(func=load_web_page)
research_planner = PlanReActPlanner()

search_agent = Agent(
    name="search_agent",
    model=DEFAULT_LLM, # Needs good reasoning and tool use
    instruction="You are a research assistant. Use the google search tool to find relevant information and URLs. ",
    tools=[google_search])

research_assistant = Agent(
    name="research_assistant_planner",
    model=DEFAULT_REASONING_LLM, # Needs good reasoning and tool use
    instruction="You are a research assistant. Create a plan to answer the user's research query. "
                "Use search to find relevant information and URLs. "
                "Use load_web_page to get content from specific URLs if needed. "
                "Synthesize the information and provide a comprehensive answer. "
                "Follow the Plan-Reason-Act-Observe cycle meticulously.",
    tools=[AgentTool(search_agent), web_page_loader_tool],
    planner=research_planner
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=research_assistant, app_name="ResearchPlannerApp")
    session_id = "s_research_plan"
    user_id = "research_user"
    create_session(runner, user_id=user_id, session_id=session_id)
    prompt = "What are the main challenges and opportunities in quantum computing today?"

    print(f"YOU: {prompt}")
    user_message = Content(parts=[Part(text=prompt)], role="user")  # User message to the agent
    print("RESEARCH_ASSISTANT (Follow trace in Dev UI for full ReAct flow):\n")

    async def main():
        # Using a set to avoid printing duplicate thought/plan sections if they are repeated
        printed_thoughts = set()
        full_final_answer_parts = []

        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    is_thought = hasattr(part, 'thought') and part.thought
                    if part.text and not is_thought:
                        print(part.text, end="", flush=True)
                        full_final_answer_parts.append(part.text)
                    elif part.text and is_thought:
                        thought_text = part.text.strip()
                        if thought_text not in printed_thoughts:
                            print(f"\n  [THOUGHT/PLAN]:\n  {thought_text}\n  ", end="", flush=True)
                            printed_thoughts.add(thought_text)
                    elif part.function_call:
                         print(f"\n  [TOOL CALL]: {part.function_call.name}({part.function_call.args})\n  ", end="", flush=True)
                    elif part.function_response:
                         print(f"\n  [TOOL RESPONSE to {part.function_response.name}]: (Content might be long, check trace)\n  ", end="", flush=True)
        print("\n\n--- Research Assistant's Combined Final Answer ---")
        print("".join(full_final_answer_parts).strip())

    asyncio.run(main())