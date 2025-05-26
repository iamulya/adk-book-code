
# tools/calculator.py
from google.adk.tools import FunctionTool
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from typing import Union 
def simple_calculator(operand1: float, operand2: float, operation: str) -> Union[float, str]: 
    """Performs a basic arithmetic operation... Args:... Returns:..."""
    if operation == 'add': return operand1 + operand2
    # ... (rest of calculator logic)
    else: return f"Error: Invalid operation '{operation}'."
calculator_tool = FunctionTool(func=simple_calculator)
calculator_agent = Agent(
    name="math_wiz", model="gemini-2.0-flash",
    instruction="You are a helpful assistant that can perform basic calculations...",
    tools=[calculator_tool]
)
if __name__ == "__main__":
    runner = InMemoryRunner(agent=calculator_agent, app_name="CalculatorApp")
    prompts = ["What is 5 plus 3?", "Calculate 10 divided by 2?"]
    for prompt_text in prompts:
        print(f"\nYOU: {prompt_text}")
        user_message = Content(parts=[Part(text=prompt_text)])
        print("MATH_WIZ: ", end="", flush=True)
        for event in runner.run(user_id="calc_user", session_id="s_calc", new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text:
                 print(event.content.parts[0].text, end="")
        print()

