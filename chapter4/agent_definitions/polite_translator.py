
# agent_definitions/polite_translator.py
from google.adk.agents import Agent
polite_translator_agent = Agent(
    name="polite_translator", model="gemini-2.0-flash",
    instruction="You are a polite translator. Translate the user's text into French. If the text is already in French, politely inform the user.",
    description="Translates English text to French politely."
)

