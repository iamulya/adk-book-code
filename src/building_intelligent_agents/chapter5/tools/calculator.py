
# tools/calculator.py
from google.adk.tools import FunctionTool
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from typing import Union 

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM

load_environment_variables()

# 1. Define the Python function
def simple_calculator(
    operand1: float,
    operand2: float,
    operation: str
) -> float | str: # Using | for Union type hint (Python 3.10+)
    """
    Performs a basic arithmetic operation on two numbers.

    Args:
        operand1: The first number.
        operand2: The second number.
        operation: The operation to perform. Must be one of 'add', 'subtract', 'multiply', 'divide'.

    Returns:
        The result of the calculation, or an error message string if the operation is invalid or division by zero occurs.
    """
    if operation == 'add':
        return operand1 + operand2
    elif operation == 'subtract':
        return operand1 - operand2
    elif operation == 'multiply':
        return operand1 * operand2
    elif operation == 'divide':
        if operand2 == 0:
            return "Error: Cannot divide by zero."
        return operand1 / operand2
    else:
        return f"Error: Invalid operation '{operation}'. Valid operations are 'add', 'subtract', 'multiply', 'divide'."
    
calculator_tool = FunctionTool(func=simple_calculator)

calculator_agent = Agent(
    name="math_wiz", model=DEFAULT_LLM,
    instruction="You are a helpful assistant that can perform basic calculations...",
    tools=[calculator_tool]
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=calculator_agent, app_name="CalculatorApp")
    prompts = ["What is 5 plus 3?", "Calculate 10 divided by 2?"]

    user_id="calc_user"
    session_id="s_calc"
    
    create_session(runner, session_id, user_id)
    
    for prompt_text in prompts:
        print(f"\nYOU: {prompt_text}")
        user_message = Content(parts=[Part(text=prompt_text)], role="user")
        print("MATH_WIZ: ", end="", flush=True)
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text:
                 print(event.content.parts[0].text, end="")
        print()