import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# can't use `from ...utils import load_environment_variables` here because of top-level import error.
def load_environment_variables():
    """
    Load environment variables from a .env file located in the parent directory of the current script.
    """
    # Ensure the .env file is loaded from the parent directory
    # Get the directory of the current script
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the .env file in the parent directory
    dotenv_path = os.path.join(current_script_dir, ".env")

    # Load the .env file if it exists
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Loaded environment variables from: {dotenv_path}")
    else:
        print(f"Warning: .env file not found at {dotenv_path}")
        
load_environment_variables()

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
    model="gemini-2.0-flash", # Use a model that supports tool use
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