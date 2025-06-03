
# llm_examples/claude_agent.py
from google.adk.agents import Agent
from google.adk.models.anthropic_llm import Claude # Import Claude
from google.adk.models.registry import LLMRegistry
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

# Register Claude model with the LLMRegistry
# This is necessary to ensure the ADK can find and use the Claude model.
LLMRegistry.register(Claude)

# Requires GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION to be set
# and access to Claude models on Vertex AI for the project.
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION") # e.g., "us-central1"
CLAUDE_MODEL_NAME = "claude-sonnet-4@20250514" # Example Claude model on Vertex AI

claude_agent = None
if GCP_PROJECT and GCP_LOCATION:
    try:
        claude_agent = Agent(
            name="claude_assistant",
            model=CLAUDE_MODEL_NAME,
            instruction="You are a helpful and thoughtful assistant powered by Claude. Provide comprehensive answers."
        )
        print(f"Claude agent initialized with model {CLAUDE_MODEL_NAME} on Vertex AI.")
    except ImportError:
        print("Anthropic SDK not found. Please install it ('pip install anthropic google-cloud-aiplatform').")
    except Exception as e:
        print(f"Could not initialize Claude model on Vertex AI: {e}")
        print("Ensure your project has access and GOOGLE_CLOUD_PROJECT/LOCATION are set.")
else:
    print("GOOGLE_CLOUD_PROJECT and/or GOOGLE_CLOUD_LOCATION not set. Skipping Claude example.")


if __name__ == "__main__":
    if claude_agent:
        runner = InMemoryRunner(agent=claude_agent, app_name="ClaudeApp")
        session_id = "s_claude"
        user_id = "claude_user"
        create_session(runner, user_id=user_id, session_id=session_id)

        user_message = Content(parts=[Part(text="Explain the concept of emergent properties in complex systems.")], role="user")
        print("\\nClaude Agent:")
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text: print(part.text, end="")
        print()

