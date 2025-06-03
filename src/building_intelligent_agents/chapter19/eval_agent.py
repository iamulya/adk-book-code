import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from building_intelligent_agents.utils import load_environment_variables, DEFAULT_LLM
load_environment_variables()  # Load environment variables for ADK configuration

# --- 1. Define a Simple Tool ---
def multiply_numbers(a: int, b: int) -> int:
  """
  Multiplies two integer numbers a and b.
  Args:
    a: The first integer.
    b: The second integer.
  Returns:
    The product of a and b.
  """
  print(f"Tool 'multiply_numbers' called with a={a}, b={b}")
  return a * b

multiply_tool = FunctionTool(func=multiply_numbers)

# --- 2. Define a Simple Agent ---
# This agent will use the 'multiply_tool'.
root_agent = Agent( 
    name="calculator_agent",
    model=DEFAULT_LLM, # Use a model that supports tool use
    instruction=(
        "You are a helpful calculator assistant. "
        "When asked to multiply numbers, use the 'multiply_numbers' tool. "
        "After using the tool, you MUST respond in the exact format: "
        "'Okay, [number1] times [number2] is [result].' "
        "Replace [number1], [number2], and [result] with the actual numbers."
    ),
    tools=[multiply_tool]
)

print(f"Agent 'calculator_agent' defined.")