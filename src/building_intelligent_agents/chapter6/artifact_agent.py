from google.adk.agents import Agent
from google.adk.tools import load_artifacts # The pre-built tool
from google.adk.tools.tool_context import ToolContext # For a custom tool to SAVE artifacts
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio # For async save_artifact in tool

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

# Custom tool to simulate saving an artifact
async def create_report_artifact(report_content: str, tool_context: ToolContext) -> dict:
    """Creates a report and saves it as an artifact."""
    filename = "summary_report.txt"
    artifact_part = Part(text=report_content)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)
    return {"status": "success", "filename_created": filename, "message": f"Report '{filename}' created and saved."}

report_creator_tool = FunctionTool(func=create_report_artifact)

artifact_handling_agent = Agent(
    name="artifact_manager",
    model=DEFAULT_LLM,
    instruction="You can create reports and then later refer to them. If a report is available, use load_artifacts to access its content if needed.",
    tools=[
        report_creator_tool,
        load_artifacts # Add the tool to make agent aware of artifacts
    ]
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=artifact_handling_agent, app_name="ArtifactApp")
    session_id = "s_artifact_test"
    user_id="artifact_user"
    create_session(runner, session_id, user_id)

    async def main():
        # Turn 1: Create an artifact
        prompt1 = "Please create a short report about ADK."
        print(f"\nYOU: {prompt1}")
        user_message1 = Content(parts=[Part(text=prompt1)], role="user")
        print("AGENT: ", end="", flush=True)
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message1):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text: print(part.text, end="")
        print()
        # Expected: Agent calls create_report_artifact. Artifact "summary_report.txt" is saved.

        # Turn 2: Ask about the artifact
        prompt2 = "What was in the report you just created?"
        print(f"\nYOU: {prompt2}")
        user_message2 = Content(parts=[Part(text=prompt2)], role="user")
        print("AGENT: ", end="", flush=True)
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message2):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text: print(part.text, end="")
        print()

    asyncio.run(main())