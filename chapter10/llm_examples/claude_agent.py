
# llm_examples/claude_agent.py
from google.adk.agents import Agent
from google.adk.models.anthropic_llm import Claude 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT"); GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
CLAUDE_MODEL_NAME = "claude-3-sonnet@20240229"; claude_agent = None
if GCP_PROJECT and GCP_LOCATION:
    try:
        claude_llm_instance = Claude(model=CLAUDE_MODEL_NAME)
        claude_agent = Agent(name="claude_assistant", model=claude_llm_instance, instruction="You are Claude.")
        print(f"Claude agent initialized with {CLAUDE_MODEL_NAME}.")
    except ImportError: print("Anthropic SDK not found.")
    except Exception as e: print(f"Could not initialize Claude: {e}")
else: print("GCP_PROJECT/LOCATION not set for Claude.")
if __name__ == "__main__":
    if claude_agent:
        runner = InMemoryRunner(agent=claude_agent, app_name="ClaudeApp")
        user_message = Content(parts=[Part(text="Explain emergent properties.")])
        print("\nClaude Agent:")
        for event in runner.run(user_id="claude_user", session_id="s_claude", new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text: print(event.content.parts[0].text, end="")
        print()

