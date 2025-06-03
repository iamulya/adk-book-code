
# telemetry_examples/configure_otel_exporter.py
# ... (full content from chapter, including setup_otel_sdk and main) ...
# For brevity in script, only showing a part. User must copy full code.
import logging; import os; from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from google.adk.agents import Agent; from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part; import asyncio
def setup_otel_sdk(service_name="adk-my-agent-app"):
    provider = TracerProvider(); console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(console_exporter))
    trace.set_tracer_provider(provider); print("OTel SDK configured with ConsoleExporter.")
# setup_otel_sdk() # User uncomments to enable
simple_agent_for_telemetry = Agent(name="telemetry_observer_agent",model=DEFAULT_LLM,instruction="Explain telemetry.")
if __name__ == "__main__":
    print("Run with `adk web .` or uncomment setup_otel_sdk() for console traces.")
    runner = InMemoryRunner(agent=simple_agent_for_telemetry, app_name="TelemetryApp")
    user_message = Content(parts=[Part(text="What is telemetry data?")])
    async def main():
        async for event in runner.run_async("otel_user", "s_otel", user_message):
            if event.content and event.content.parts[0].text: print(f"AGENT: {event.content.parts[0].text.strip()}")
    asyncio.run(main())

