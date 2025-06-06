from google.adk.agents import Agent
try:
    from google.adk.models.lite_llm import LiteLlm
    LITELLM_AVAILABLE = True
except ImportError: 
    LITELLM_AVAILABLE = False

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import requests # To check if Ollama is running

from building_intelligent_agents.utils import create_session

ollama_agent = None
if LITELLM_AVAILABLE:
    # Check if Ollama server is accessible
    ollama_running = False
    try:
        # Default Ollama API endpoint
        response = requests.get("<http://localhost:11434>")
        if response.status_code == 200 and "Ollama is running" in response.text:
            ollama_running = True
            print("Ollama server detected.")
        else:
            print("Ollama server found but not responding as expected.")
    except requests.exceptions.ConnectionError:
        print("Ollama server not found at <http://localhost:11434>. Please ensure Ollama is installed and running.")

    if ollama_running:
        try:
            # For Ollama, prefix the model name with "ollama/"
            # This assumes you have 'llama3' model pulled via `ollama pull llama3`
            ollama_llm_instance = LiteLlm(model="ollama/llama3")
            # You can also specify the full API base if Ollama runs elsewhere:
            # ollama_llm_instance = LiteLlm(model="ollama/llama3", api_base="<http://my-ollama-server:11434>")

            ollama_agent = Agent(
                name="local_llama3_assistant",
                model=ollama_llm_instance,
                instruction="You are a helpful assistant running locally via Ollama and Llama 3."
            )
            print("Ollama Llama3 agent (via LiteLLM) initialized.")
        except Exception as e:
            print(f"Error initializing LiteLlm agent for Ollama: {e}")
            print("Ensure you have pulled the model (e.g., 'ollama pull llama3').")
else:
    print("Skipping LiteLLM Ollama example as LiteLLM library is not available.")

if __name__ == "__main__":
    if ollama_agent:
        runner = InMemoryRunner(agent=ollama_agent, app_name="LiteLLM_Ollama_App")
        session_id="s_ollama"
        user_id="ollama_user"
        create_session(runner, user_id=user_id, session_id=session_id)

        user_message = Content(parts=[Part(text="Why is the sky blue? Explain briefly.")], role="user")
        print("\\nLocal Llama3 Agent (via LiteLLM and Ollama):")

        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text:
                print(event.content.parts[0].text, end="")
        print()
    else:
        print("Ollama agent not run due to setup issues.")