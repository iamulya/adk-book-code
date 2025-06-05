from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool # Import the tool
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import os

from building_intelligent_agents.utils import create_session, DEFAULT_LLM

# This requires a Google Cloud Project and a configured Vertex AI Search data store.
# Ensure your environment is authenticated for GCP (e.g., via `gcloud auth application-default login`)
# and the necessary APIs are enabled (Vertex AI API, Search API).

# Furthermore, upload the document from https://arxiv.org/abs/2505.24832 in a GCP bucket.
# Subsequently, create a data store using this bucket and wait until the document is imported into the data store

# Replace with your actual project, location, and data store ID
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1") 

# Example Data Store ID format: projects/<PROJECT_ID>/locations/<LOCATION>/collections/default_collection/dataStores/<DATA_STORE_ID>
DATA_STORE_ID = os.getenv("VERTEX_AI_SEARCH_DATA_STORE_ID")

if not all([GCP_PROJECT, DATA_STORE_ID]):
    print("Error: GOOGLE_CLOUD_PROJECT and VERTEX_AI_SEARCH_DATA_STORE_ID environment variables must be set.")
    # exit() # Uncomment to make it a hard stop

# Initialize the tool with your data store ID
if DATA_STORE_ID:
    llm_knowledge_tool = VertexAiSearchTool(data_store_id=DATA_STORE_ID)

    llm_knowledge_agent = Agent(
        name="llm_knowledge_agent",
        model=DEFAULT_LLM, # Requires a model that supports Vertex AI Search tool
        instruction="You are an expert on LLM memories. Use the provided search tool to answer the user queries.",
        tools=[llm_knowledge_tool]
    )

    if __name__ == "__main__":
        if not DATA_STORE_ID:
            print("Skipping VertexAiSearchTool example as DATA_STORE_ID is not set.")
        else:
            runner = InMemoryRunner(agent=llm_knowledge_agent, app_name="LlmKnowledgeApp")
            session_id = "s_llm_knowledge"
            user_id = "emp123"
            create_session(runner, session_id, user_id)

            prompt = "What is double descent phenomenon"
            print(f"\\nYOU: {prompt}")
            user_message = Content(parts=[Part(text=prompt)], role="user")
            print("ASSISTANT: ", end="", flush=True)
            for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
                    if event.grounding_metadata and event.grounding_metadata.retrieval_queries:
                         print(f"\\n  (Retrieved from Vertex AI Search with queries: {event.grounding_metadata.retrieval_queries})", end="")
            print()
else:
    print("Skipping VertexAiSearchTool agent definition as DATA_STORE_ID is not set.")
    llm_knowledge_agent = None # Define it as None if not configured
