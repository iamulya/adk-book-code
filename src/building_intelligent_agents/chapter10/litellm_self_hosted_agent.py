from google.adk.agents import Agent
try:
    from google.adk.models.lite_llm import LiteLlm
    LITELLM_AVAILABLE = True
except ImportError: 
    LITELLM_AVAILABLE = False

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os
import requests

from building_intelligent_agents.utils import create_session

# Assume you have a self-hosted LLM (e.g., using TGI or vLLM)
# serving an OpenAI-compatible API at this base URL.
SELF_HOSTED_API_BASE = os.getenv("MY_SELF_HOSTED_LLM_API_BASE", "<http://localhost:8000/v1>") # Example for local TGI
# The model name here is often arbitrary for self-hosted endpoints but might be
# used by LiteLLM or the endpoint itself for routing if it serves multiple models.
# For TGI/vLLM, it's often just the "model" you want to hit at that endpoint.
SELF_HOSTED_MODEL_NAME = os.getenv("MY_SELF_HOSTED_LLM_MODEL_NAME", "custom/my-model")

self_hosted_agent = None
if LITELLM_AVAILABLE:
    # Check if the self-hosted endpoint is accessible
    endpoint_running = False
    try:
        # A simple check - a real check might query a /health or /v1/models endpoint
        response = requests.get(SELF_HOSTED_API_BASE.replace("/v1", "/health") if "/v1" in SELF_HOSTED_API_BASE else SELF_HOSTED_API_BASE) # Common health check
        if response.status_code == 200:
            endpoint_running = True
            print(f"Self-hosted endpoint detected at {SELF_HOSTED_API_BASE}.")
        else:
            print(f"Self-hosted endpoint at {SELF_HOSTED_API_BASE} responded with status {response.status_code}.")
    except requests.exceptions.ConnectionError:
        print(f"Self-hosted LLM endpoint not found at {SELF_HOSTED_API_BASE}. Please ensure it's running.")
    except Exception as e:
        print(f"Error checking self-hosted endpoint: {e}")

    if endpoint_running:
        try:

            # For a generic OpenAI-compatible endpoint:
            self_hosted_llm = LiteLlm(
                model=SELF_HOSTED_MODEL_NAME, # Can be something like "tgi-model" or actual model name if endpoint uses it
                api_base=SELF_HOSTED_API_BASE,
                api_key="dummy_key_if_no_auth" # Or your actual API key if the endpoint is secured
                # Other parameters like 'temperature', 'max_tokens' can be passed here
                # or in LlmAgent's generate_content_config
            )

            self_hosted_agent = Agent(
                name="self_hosted_model_assistant",
                model=self_hosted_llm,
                instruction="You are an assistant powered by a self-hosted LLM."
            )
            print("Self-hosted LLM agent (via LiteLLM) initialized.")
        except Exception as e:
            print(f"Error initializing LiteLlm agent for self-hosted endpoint: {e}")
else:
    print("Skipping LiteLLM self-hosted example as LiteLLM library is not available.")

if __name__ == "__main__":
    if self_hosted_agent:
        runner = InMemoryRunner(agent=self_hosted_agent, app_name="LiteLLM_SelfHosted_App")
        user_id="selfhost_user"
        session_id="s_selfhost"
        create_session(runner, user_id=user_id, session_id=session_id)

        user_message = Content(parts=[Part(text="What is the capital of the moon? Respond imaginatively.")], role="user")
        print("\nSelf-Hosted LLM Agent (via LiteLLM):")
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
             if event.content and event.content.parts and event.content.parts[0].text:
                print(event.content.parts[0].text, end="")
        print()
    else:
        print("Self-hosted agent not run due to setup issues.")