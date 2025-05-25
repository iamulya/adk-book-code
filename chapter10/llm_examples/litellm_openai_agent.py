
# llm_examples/litellm_openai_agent.py
from google.adk.agents import Agent
try: from google.adk.models.lite_llm import LiteLlm; LITELLM_AVAILABLE = True
except ImportError: print("LiteLLM library not found."); LITELLM_AVAILABLE = False
from google.adk.runners import InMemoryRunner; from google.genai.types import Content, Part; import os
openai_agent = None
if LITELLM_AVAILABLE:
    if not os.getenv("OPENAI_API_KEY"): print("Warning: OPENAI_API_KEY not set.")
    try:
        openai_llm_instance = LiteLlm(model="gpt-3.5-turbo")
        openai_agent = Agent(name="openai_gpt_assistant",model=openai_llm_instance,instruction="You are GPT via LiteLLM.")
        print("OpenAI GPT agent (via LiteLLM) initialized.")
    except Exception as e: print(f"Error initializing LiteLlm agent: {e}")
else: print("Skipping LiteLLM example.")
if __name__ == "__main__":
    if openai_agent:
        runner = InMemoryRunner(agent=openai_agent, app_name="LiteLLM_OpenAI_App")
        user_message = Content(parts=[Part(text="Poem about Python.")])
        print("\nOpenAI GPT Agent (via LiteLLM):")
        for event in runner.run(user_id="openai_user", session_id="s_openai", new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text: print(event.content.parts[0].text, end="")
        print()

