
# flows_planners_examples/builtin_planner_agent.py
from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner 
from google.genai.types import ThinkingConfig, Tool 
from google.adk.tools import FunctionTool 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os; import asyncio; import logging
logger = logging.getLogger(__name__)
def get_product_price(product_id: str) -> dict:
    """Gets price for product ID."""
    prices = {"prod123": 29.99, "prod456": 49.50}
    return {"product_id": product_id, "price": prices[product_id]} if product_id in prices else {"error": "Product not found"}
price_tool = FunctionTool(func=get_product_price)
product_thinking_config = ThinkingConfig(
    reasoning_mode=ThinkingConfig.ReasoningMode.REASONING_MODE_PROMPT, 
    tool_mode=ThinkingConfig.ToolMode.TOOL_MODE_ENABLED, max_iterations=5
)
builtin_item_planner = BuiltInPlanner(thinking_config=product_thinking_config)
agent_with_builtin_planner = Agent(
    name="smart_shopper_builtin", model="gemini-1.5-pro-latest", 
    instruction="Help user find product prices. Think step-by-step and use tools.",
    tools=[price_tool], planner=builtin_item_planner
)
if __name__ == "__main__":
    runner = InMemoryRunner(agent=agent_with_builtin_planner, app_name="BuiltInPlanApp")
    prompt = "Price of prod123 and then prod456?"
    print(f"YOU: {prompt}"); user_message = Content(parts=[Part(text=prompt)])
    print("ASSISTANT: ", end="", flush=True)
    async def main():
        async for event in runner.run_async(user_id="plan_user", session_id="s_builtinplan", new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text: print(part.text, end="", flush=True)
                    elif hasattr(part, 'thought') and part.thought: print(f"\n  [THOUGHT]: {part.text.strip() if part.text else 'No text in thought']}\n  ", end="")
                    elif part.function_call: print(f"\n  [TOOL CALL]: {part.function_call.name}({part.function_call.args})\n  ", end="")
                    elif part.function_response: print(f"\n  [TOOL RESPONSE to {part.function_response.name}]: {part.function_response.response}\n  ", end="")
        print()
    asyncio.run(main())

