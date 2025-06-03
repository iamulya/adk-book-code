import logging
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter # Simple console exporter
# For Google Cloud Trace, you would use:
# from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
# from opentelemetry.sdk.resources import Resource
# from opentelemetry.semconv.resource import ResourceAttributes

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio

from building_intelligent_agents.utils import DEFAULT_LLM, load_environment_variables  
load_environment_variables()  # Load environment variables for ADK configuration

# --- Configure OpenTelemetry SDK ---
# This setup should ideally happen once at the beginning of your application.
def setup_otel_sdk(service_name="adk-my-agent-app"):
    provider = TracerProvider(
        # For Cloud Trace, you'd add a resource:
        # resource=Resource.create({
        #     ResourceAttributes.SERVICE_NAME: service_name,
        #     "gcp.project.id": os.getenv("GOOGLE_CLOUD_PROJECT") # Important for Cloud Trace
        # })
    )

    # Export to console for this example
    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(console_exporter))

    # For Google Cloud Trace:
    # if os.getenv("GOOGLE_CLOUD_PROJECT"):
    #     cloud_trace_exporter = CloudTraceSpanExporter(
    #         project_id=os.getenv("GOOGLE_CLOUD_PROJECT")
    #     )
    #     provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))
    #     print(f"OpenTelemetry configured to export to Google Cloud Trace project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    # else:
    #     print("GOOGLE_CLOUD_PROJECT not set, Cloud Trace exporter not configured.")

    # Set the global tracer provider
    trace.set_tracer_provider(provider)
    print("OpenTelemetry SDK configured with ConsoleSpanExporter.")

# Call setup at the start of your application
# setup_otel_sdk() # Uncomment to enable console exporting of spans

# --- Your ADK Agent ---
simple_agent_for_telemetry = Agent(
    name="telemetry_observer_agent",
    model=DEFAULT_LLM,  # Use your preferred model
    instruction="Briefly explain what telemetry is."
)

if __name__ == "__main__":
    # Important: Call setup_otel_sdk() *before* any ADK runner or agent operations
    # if you want to capture their traces with your custom exporter.
    # If you don't call it, ADK uses a default no-op tracer provider unless the Dev UI sets one up.
    # The Dev UI itself configures an in-memory exporter to populate its Trace view.

    print("Running agent. If OpenTelemetry SDK with ConsoleExporter is set up (uncomment setup_otel_sdk()), spans will print to console.")
    print("Otherwise, use `adk web .` and check the Trace view in the Dev UI.\\n")

    runner = InMemoryRunner(agent=simple_agent_for_telemetry, app_name="TelemetryApp")
    user_message = Content(parts=[Part(text="What is telemetry data?")])

    async def main():
        async for event in runner.run_async(user_id="otel_user", session_id="s_otel", new_message=user_message):
            if event.content and event.content.parts[0].text:
                print(f"AGENT: {event.content.parts[0].text.strip()}")

    asyncio.run(main())

    # If you had setup_otel_sdk() uncommented and ran this script,
    # you would see JSON representations of spans printed to your console
    # by the ConsoleSpanExporter. These would look something like:
    # {
    #     "name": "agent_run [telemetry_observer_agent]",
    #     "context": { ... trace_id, span_id ... },
    #     "kind": "SpanKind.INTERNAL",
    #     "parent_id": "...",
    #     "start_time": "...",
    #     "end_time": "...",
    #     "status": { ... },
    #     "attributes": {
    #         "gen_ai.system": "gcp.vertex.agent",
    #         "gcp.vertex.agent.invocation_id": "e-xxxx", ...
    #     },
    #     ...
    # }