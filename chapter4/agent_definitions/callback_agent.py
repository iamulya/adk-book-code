
# agent_definitions/callback_agent.py
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai.types import Content, Part
from typing import Optional 
import logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

def my_before_agent_cb(context: CallbackContext) -> Optional[Content]:
    logger.info(f"[{context.agent_name}] In before_agent_callback. Invocation ID: {context.invocation_id}")
    if "block_user" in context.state.get("user:flags", []):
        logger.warning(f"[{context.agent_name}] User is blocked. Skipping agent run.")
        return Content(parts=[Part(text="I'm sorry, I cannot process your request at this time.")])
    return None
async def my_before_model_cb(context: CallbackContext, request: LlmRequest) -> Optional[LlmResponse]:
    logger.info(f"[{context.agent_name}] In before_model_callback. Modifying request.")
    if request.contents and request.contents[-1].role == "user":
        request.contents[-1].parts[0].text = f"Consider this: {request.contents[-1].parts[0].text}"
    return None
def my_after_model_cb(context: CallbackContext, response: LlmResponse) -> Optional[LlmResponse]:
    logger.info(f"[{context.agent_name}] In after_model_callback.")
    if response.content and response.content.parts and response.content.parts[0].text:
        response.content.parts[0].text += " (Processed by after_model_callback)"
    response.custom_metadata = {"source": "after_model_cb_modification"}
    return response
callback_demo_agent = Agent(
    name="callback_demo_agent", model="gemini-1.5-flash-latest",
    instruction="You are an echo agent. Repeat the user's message.",
    description="Demonstrates agent and model callbacks.",
    before_agent_callback=my_before_agent_cb,
    before_model_callback=my_before_model_cb,
    after_model_callback=my_after_model_cb
)
if __name__ == "__main__":
    from google.adk.runners import InMemoryRunner
    runner = InMemoryRunner(agent=callback_demo_agent, app_name="CallbackApp")
    print("\n--- Scenario 1: Normal Run ---")
    user_message1 = Content(parts=[Part(text="Hello ADK!")])
    for event in runner.run(user_id="cb_user", session_id="s_normal", new_message=user_message1):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: print(part.text, end="")
            if event.custom_metadata: print(f" [Metadata: {event.custom_metadata}]", end="")
    print()
    print("\n--- Scenario 2: User Blocked ---")
    user_message2 = Content(parts=[Part(text="Another message.")])
    blocked_user_session_id = "s_blocked"
    runner.session_service._create_session_impl(
        app_name="CallbackApp", user_id="cb_user_blocked",
        session_id=blocked_user_session_id, state={"user:flags": ["block_user"]}
    )
    for event in runner.run(user_id="cb_user_blocked", session_id=blocked_user_session_id, new_message=user_message2):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: print(part.text, end="")
    print()

