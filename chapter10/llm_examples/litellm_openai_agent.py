
# llm_examples/litellm_openai_agent.py
from google.adk.agents import Agent
# Ensure litellm is installed: pip install google-adk[extensions] or pip install litellm
try:
    from google.adk.models.lite_llm import LiteLlm # Key import
    LITELLM_AVAILABLE = True
except ImportError:
    print("LiteLLM library not found. Please install it ('pip install litellm').")
    LITELLM_AVAILABLE = False

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os
from ...utils import load_environment_variables, create_session
load_environment_variables()

openai_agent = None
if LITELLM_AVAILABLE:
    # Requires OPENAI_API_KEY environment variable to be set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set. LiteLLM OpenAI example may fail.")

    try:
        # Specify the model using litellm's naming convention (e.g., "openai/gpt-3.5-turbo")
        openai_llm_instance = LiteLlm(model="gpt-3.5-turbo") # For OpenAI, use "gpt-..."
                                                          # For Azure OpenAI: "azure/your-deployment-name"
                                                          # For Cohere: "cohere/command-r"
                                                          # etc.

        openai_agent = Agent(
            name="openai_gpt_assistant",
            model=openai_llm_instance,
            instruction="You are a helpful assistant powered by an OpenAI model via LiteLLM."
        )
        print("OpenAI GPT agent (via LiteLLM) initialized.")
    except Exception as e:
        print(f"Error initializing LiteLlm agent: {e}")
else:
    print("Skipping LiteLLM example as the library is not available.")


if __name__ == "__main__":
    if openai_agent:
        runner = InMemoryRunner(agent=openai_agent, app_name="LiteLLM_OpenAI_App")
        session_id = "s_openai"
        user_id = "openai_user"
        create_session(runner, user_id=user_id, session_id=session_id)

        user_message = Content(parts=[Part(text="Write a short poem about Python programming.")], role="user")  
        print("\\nOpenAI GPT Agent (via LiteLLM):")
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text: print(part.text, end="")
        print()
