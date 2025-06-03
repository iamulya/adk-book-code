# flows_planners_examples/builtin_planner_agent.py
from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner # Key import
from google.genai.types import ThinkingConfig # For ThinkingConfig
from google.adk.tools import FunctionTool # Example tool
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

def get_product_price(product_id: str) -> dict:
    """Gets the price for a given product ID."""
    prices = {"prod123": 29.99, "prod456": 49.50}
    if product_id in prices:
        return {"product_id": product_id, "price": prices[product_id]}
    return {"error": "Product not found"}

price_tool = FunctionTool(func=get_product_price)

# Configure the built-in thinking
product_thinking_config = ThinkingConfig(include_thoughts=True)

# Create the planner
builtin_item_planner = BuiltInPlanner(thinking_config=product_thinking_config)

agent_with_builtin_planner = Agent(
    name="smart_shopper_builtin",
    model="DEFAULT_REASONING_LLM", # Ensure this model supports ThinkingConfig
    instruction="You are an assistant helping a user find product prices. Think step-by-step and use tools.",
    tools=[price_tool],
    planner=builtin_item_planner # Assign the planner
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=agent_with_builtin_planner, app_name="BuiltInPlanApp")
    session_id = "s_builtinplan"
    user_id = "plan_user"
    create_session(runner, user_id=user_id, session_id=session_id)

    prompt = "What's the price of product prod123 and then prod456?"

    print(f"YOU: {prompt}")
    user_message = Content(parts=[Part(text=prompt)], role="user")  # User message to the agent
    print("ASSISTANT: ", end="", flush=True)

    async def main():
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
                    elif hasattr(part, 'thought') and part.thought: # Check if part is a thought
                        print(f"\\n  [THOUGHT]: {part.text.strip() if part.text else 'No text in thought'}\\n  ", end="")
                    # Also print tool calls/responses for clarity if they appear as separate events
                    elif part.function_call:
                         print(f"\\n  [TOOL CALL]: {part.function_call.name}({part.function_call.args})\\n  ", end="")
                    elif part.function_response:
                         print(f"\\n  [TOOL RESPONSE to {part.function_response.name}]: {part.function_response.response}\\n  ", end="")
        print()

    import asyncio
    asyncio.run(main())