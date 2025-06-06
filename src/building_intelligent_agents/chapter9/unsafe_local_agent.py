from google.adk.agents import Agent
from google.adk.code_executors import UnsafeLocalCodeExecutor # Key import
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

# ⚠️ DANGER ⚠️: UnsafeLocalCodeExecutor executes arbitrary code from the LLM
# in your local Python environment. ONLY use this in trusted development
# environments and NEVER in production or with untrusted LLM outputs.

unsafe_code_agent = Agent(
    name="unsafe_code_agent",
    model=DEFAULT_LLM, # Can be any model that generates code
    instruction="You are an assistant that can write Python code to solve problems. I will execute the code you provide in my local environment. Focus on simple calculations that don't require external libraries beyond standard Python.",
    code_executor=UnsafeLocalCodeExecutor() # Assign the executor
)

if __name__ == "__main__":
    print("⚠️ WARNING: Running UnsafeLocalCodeExecutor. This is not recommended for production. ⚠️")
    runner = InMemoryRunner(agent=unsafe_code_agent, app_name="UnsafeCodeApp")
    session_id = "s_unsafe_code_test"
    user_id = "unsafe_user"
    create_session(runner, session_id, user_id)
    prompts = [
        "Define a variable x as 10 and y as 20, then print their sum.",
        "What is 2 to the power of 10?",
    ]

    async def main():
        for prompt_text in prompts:
            print(f"\nYOU: {prompt_text}")
            user_message = Content(parts=[Part(text=prompt_text)], role="user")
            print("ASSISTANT (via UnsafeLocalCodeExecutor): ", end="", flush=True)
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
                # Trace: LLM -> code -> UnsafeLocalCodeExecutor.execute_code() -> result -> LLM -> final text
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text: print(part.text, end="", flush=True)
                        # We might not see executable_code/code_execution_result directly in the final agent output
                        # if the LLM summarizes it, but they'll be in the Trace.
            print()

    import asyncio
    asyncio.run(main())