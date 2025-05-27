
# tools/calculator.py
import asyncio
from google.adk.tools import FunctionTool
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from typing import Union 

from ...utils import load_environment_variables

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
    name="math_wiz", model="gemini-2.0-flash",
    instruction="You are a helpful assistant that can perform basic calculations...",
    tools=[calculator_tool]
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=calculator_agent, app_name="CalculatorApp")
    prompts = ["What is 5 plus 3?", "Calculate 10 divided by 2?"]

    user_id="calc_user"
    session_id="s_calc"
    
    # --- Create the session before the loop ---
    print(f"Creating session: {session_id} for user: {user_id} on app: {runner.app_name}")
    # Since session_service.create_session is async, we need to run it in an event loop
    try:
        asyncio.run(runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        ))
        print("Session created successfully.")
    except Exception as e:
        print(f"Error creating session: {e}")
        exit()
    # --- Session creation done ---
    
    for prompt_text in prompts:
        print(f"\nYOU: {prompt_text}")
        user_message = Content(parts=[Part(text=prompt_text)], role="user")
        print("MATH_WIZ: ", end="", flush=True)
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text:
                 print(event.content.parts[0].text, end="")
        print()

