
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset 
from mcp import StdioServerParameters 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os
import asyncio

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

filesystem_mcp_params = StdioServerParameters(
    command='npx', args=["-y", "@modelcontextprotocol/server-filesystem", "."]
)
mcp_fs_toolset = None

try:
    mcp_fs_toolset = MCPToolset(connection_params=filesystem_mcp_params)
except ImportError:
    print("MCP Toolset requires Python 3.10+ and 'mcp' package.")
    print("Also ensure Node.js and npx are available for this example.")

mcp_agent = None
if mcp_fs_toolset:
    mcp_agent = Agent(
        name="filesystem_navigator", model=DEFAULT_LLM,
        instruction="Interact with local filesystem using tools (listFiles, readFile, writeFile).",
        tools=[mcp_fs_toolset]
    )

if __name__ == "__main__":
    runner = InMemoryRunner(agent=mcp_agent, app_name="ArtifactApp")
    session_id = "s_artifact_test"
    user_id="artifact_user"
    create_session(runner, session_id, user_id)

    async def main():
        if not mcp_agent:
            print("MCP Agent not initialized. Skipping example.")
            return

        test_file_content = "Hello from ADK to MCP!"
        test_filename = "mcp_test_file.txt"

        with open(test_filename, "w") as f: f.write(test_file_content)
        prompts = [ f"Contents of '{test_filename}'?"]
        for prompt_text in prompts:
            print(f"\nYOU: {prompt_text}")
            user_message = Content(parts=[Part(text=prompt_text)], role="user")
            print("FILESYSTEM_NAVIGATOR: ", end="", flush=True)
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
                if event.content and event.content.parts and event.content.parts[0].text:
                    print(event.content.parts[0].text, end="")
            print()
        if os.path.exists(test_filename): os.remove(test_filename)
        if mcp_fs_toolset: # Ensure it was initialized before trying to close
            print("\nClosing MCP toolset...")
            await mcp_fs_toolset.close()
            print("MCP toolset closed.")

    asyncio.run(main())