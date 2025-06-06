# runner_examples/run_config_demo.py
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner, RunConfig
from google.adk.agents.run_config import StreamingMode
from google.genai.types import SpeechConfig, Content, Part # For speech and transcription
import asyncio

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()  # Load environment variables for ADK configuration

# This example is conceptual for some features like speech, as they require
# actual audio input/output capabilities not easily shown in a text script.

story_agent = Agent(
    name="story_teller",
    model=DEFAULT_LLM,
    instruction="Tell a very short, one-sentence story."
)
runner = InMemoryRunner(agent=story_agent, app_name="ConfigDemoApp")
session_id = "s_user_rc"  # Session ID for the user
user_id = "user_rc"  # User ID for the session
create_session(runner, user_id=user_id, session_id=session_id)  # Create a session for the user

user_input_message = Content(parts=[Part(text="A story please.")], role="user")  # User's input message to the agent

async def demo_run_configs():
    # Scenario 1: Default RunConfig (no streaming)
    print("\n--- Scenario 1: Default (No Streaming) ---")
    default_config = RunConfig()
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_input_message, run_config=default_config):
        if event.content and event.content.parts[0].text: print(event.content.parts[0].text.strip())

    # Scenario 2: SSE Streaming
    print("\n--- Scenario 2: SSE Streaming ---")
    sse_config = RunConfig(streaming_mode=StreamingMode.SSE)
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_input_message, run_config=sse_config):
        if event.content and event.content.parts[0].text:
            print(event.content.parts[0].text, end="", flush=True) # Print chunks
    print()

    # Scenario 3: Limiting LLM Calls (Conceptual)
    # This agent doesn't make many calls, but shows the config
    print("\n--- Scenario 3: Max LLM Calls (Conceptual) ---")
    # If agent tries more than 1 LLM call, LlmCallsLimitExceededError would be raised by InvocationContext
    # For this simple agent, it will likely make only 1 call.
    limit_config = RunConfig(max_llm_calls=1)
    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_input_message, run_config=limit_config):
            if event.content and event.content.parts[0].text: print(event.content.parts[0].text.strip())
    except Exception as e: # Catching generic Exception for demo
        print(f"  Caught expected error due to max_llm_calls: {type(e).__name__} - {e}")

    # Scenario 4: Input Blobs as Artifacts (Conceptual)
    print("\n--- Scenario 4: Save Input Blobs as Artifacts (Conceptual) ---")
    artifact_config = RunConfig(save_input_blobs_as_artifacts=True)
    # If user_input_message contained a Part with inline_data (e.g., an image),
    # the Runner would save it to the ArtifactService before passing to agent.
    # The agent would see a text part like "Uploaded file: artifact_..."
    # This requires an ArtifactService to be configured with the Runner.
    # runner_with_artifacts = Runner(..., artifact_service=InMemoryArtifactService())
    # await runner_with_artifacts.run_async(..., run_config=artifact_config, new_message=message_with_blob)
    print("  (This would save input blobs to ArtifactService if message contained them and ArtifactService was active)")

    # Scenario 5: Compositional Function Calling (CFC) - Experimental for SSE
    # Requires a model supporting CFC (e.g., Gemini 2.0+ via LIVE API)
    # and BuiltInCodeExecutor or tools that benefit from it.
    # print("\n--- Scenario 5: Compositional Function Calling (CFC) via SSE ---")
    # cfc_config = RunConfig(
    #     support_cfc=True,
    #     streaming_mode=StreamingMode.SSE # CFC currently implies SSE via LIVE API usage
    # )
    # An agent using BuiltInCodeExecutor or complex tools would benefit.
    # For this simple agent, it won't show much difference in output.
    # The underlying LLM call mechanism changes to use the LIVE API.
    # print("  (Agent would use LIVE API for potential CFC if tools/code exec were involved)")
    # async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_input_message, run_config=cfc_config):
    #     if event.content and event.content.parts[0].text: print(event.content.parts[0].text.strip())

    # Scenario 6: Bidirectional Streaming (BIDI) with Speech & Transcription - Highly Conceptual for CLI
    # This is for `runner.run_live()` and requires actual audio streams.
    # print("\n--- Scenario 6: BIDI Streaming with Speech & Transcription (Conceptual for CLI) ---")
    # bidi_config = RunConfig(
    #     streaming_mode=StreamingMode.BIDI,
    #     speech_config=SpeechConfig(
    #         # See google.genai.types.SpeechConfig for options
    #         # Example: engine="chirp_universal", language_codes=["en-US"]
    #     ),
    #     response_modalities=["AUDIO", "TEXT"], # Agent can respond with audio and/or text
    #     output_audio_transcription=AudioTranscriptionConfig(), # Get text of agent's audio
    #     input_audio_transcription=AudioTranscriptionConfig() # Transcribe user's audio input
    # )
    # print(f"  Configured for BIDI: {bidi_config.model_dump_json(indent=2, exclude_none=True)}")
    # To use this:
    # from google.adk.agents.live_request_queue import LiveRequestQueue
    # live_queue = LiveRequestQueue()
    # # In a real app, you'd feed audio chunks to live_queue.send_realtime(Blob(...))
    # async for event in runner.run_live(..., live_request_queue=live_queue, run_config=bidi_config):
    #     # Process events, which might include audio blobs or transcriptions
    # live_queue.close()
    print("  (Actual run_live with BIDI/speech needs real audio input/output handling)")

if __name__ == "__main__":
    asyncio.run(demo_run_configs())
