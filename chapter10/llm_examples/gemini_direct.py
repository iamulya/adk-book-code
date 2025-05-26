
# llm_examples/gemini_direct.py
from google.adk.agents import Agent
from google.adk.models import Gemini 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os
if not os.getenv("GOOGLE_API_KEY"): print("Error: GOOGLE_API_KEY not set."); exit()
gemini_agent_auto = Agent(name="gemini_auto_resolver", model="gemini-2.0-flash", instruction="You are Gemini.")
gemini_llm_instance = Gemini(model="gemini-2.0-flash")
gemini_agent_explicit = Agent(name="gemini_explicit_instance", model=gemini_llm_instance, instruction="You are Gemini via instance.")
if __name__ == "__main__":
    runner = InMemoryRunner(agent=gemini_agent_auto, app_name="GeminiApp") 
    user_message = Content(parts=[Part(text="Fun fact about LLMs?")])
    print("Gemini Agent (auto-resolved):")
    for event in runner.run(user_id="gem_user", session_id="s_gem_auto", new_message=user_message):
        if event.content and event.content.parts and event.content.parts[0].text: print(event.content.parts[0].text, end="")
    print("\n")

