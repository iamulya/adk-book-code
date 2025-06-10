from google.adk.agents import LlmAgent # LlmAgent is an alias for Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

def echo_user_input(callback_context: CallbackContext) -> types.Content:
    """
    A simple callback that takes the user's input and echoes it back.
    """
    user_message = ""
    invocation_ctx = getattr(callback_context, '_invocation_context', None)
    if invocation_ctx and hasattr(invocation_ctx, 'user_content') and invocation_ctx.user_content:
        if invocation_ctx.user_content.parts and invocation_ctx.user_content.parts[0].text:
            user_message = invocation_ctx.user_content.parts[0].text

    response_text = f"Echo Agent says: You sent '{user_message}'"
    return types.Content(parts=[types.Part(text=response_text)])

root_agent = LlmAgent(
    name="simple_echo_agent",
    # Even though we use a callback, a model is usually expected.
    # For Vertex AI, it will try to use this model based on .env settings.
    model="gemini-2.0-flash",
    instruction="You are an echo agent. You repeat what the user says with a prefix.",
    description="A simple agent that echoes user input.",
    before_agent_callback=echo_user_input
)