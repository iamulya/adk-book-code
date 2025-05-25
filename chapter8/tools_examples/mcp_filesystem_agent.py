
# tools_examples/mcp_filesystem_agent.py
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset 
from mcp import StdioServerParameters 
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os
import asyncio

filesystem_mcp_params = StdioServerParameters(
    command='npx', args=["-y", "@modelcontextprotocol/server-filesystem"]
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
        name="filesystem_navigator", model="gemini-1.5-flash-latest",
        instruction="Interact with local filesystem using tools (listFiles, readFile, writeFile).",
        tools=[mcp_fs_toolset]
    )
async def main_async(): # Renamed from if __name__ == "__main__":
    if not mcp_agent:
        print("MCP Agent not initialized. Skipping example.")
        return
    runner = InMemoryRunner(agent=mcp_agent, app_name="MCP_FS_App")
    test_file_content = "Hello from ADK to MCP!"
    test_filename = "mcp_test_file.txt"
    with open(test_filename, "w") as f: f.write(test_file_content)
    prompts = [ f"List files in current directory?", f"Contents of '{test_filename}'?"]
    for prompt_text in prompts:
        print(f"\nYOU: {prompt_text}")
        user_message = Content(parts=[Part(text=prompt_text)])
        print("FILESYSTEM_NAVIGATOR: ", end="", flush=True)
        async for event in runner.run_async(user_id="mcp_user", session_id="s_mcp_fs", new_message=user_message):
            if event.content and event.content.parts and event.content.parts[0].text:
                 print(event.content.parts[0].text, end="")
        print()
    if os.path.exists(test_filename): os.remove(test_filename)
    if mcp_fs_toolset: # Ensure it was initialized before trying to close
        print("\nClosing MCP toolset...")
        await mcp_fs_toolset.close()
        print("MCP toolset closed.")
if __name__ == "__main__": # This part remains to call the async main
    asyncio.run(main_async())

