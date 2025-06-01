# runner_examples/custom_runner_setup.py
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.artifacts import InMemoryArtifactService, GcsArtifactService
from google.adk.memory import InMemoryMemoryService
import os

# Define a simple agent
my_root_agent = Agent(
    name="main_app_agent",
    model="gemini-2.0-flash",
    instruction="You are the main agent for this application."
)

# Option 1: Using all InMemory services (similar to InMemoryRunner)
in_memory_session_svc = InMemorySessionService()
in_memory_artifact_svc = InMemoryArtifactService()
in_memory_memory_svc = InMemoryMemoryService()

runner_in_memory = Runner(
    app_name="MyInMemoryApp",
    agent=my_root_agent,
    session_service=in_memory_session_svc,
    artifact_service=in_memory_artifact_svc,
    memory_service=in_memory_memory_svc
)
print(f"Runner initialized with InMemory services for app: {runner_in_memory.app_name}")

# Option 2: Using persistent services (conceptual, requires setup)
# Ensure GOOGLE_CLOUD_PROJECT and potentially other env vars are set for GCS/Database
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "my-gcp-project")
GCS_BUCKET_NAME = os.getenv("ADK_ARTIFACT_GCS_BUCKET", "my-adk-artifacts-bucket")
# Example: "mysql+pymysql://user:pass@host/db" or "sqlite:///./my_adk_sessions.db"
DATABASE_URL = os.getenv("ADK_DATABASE_URL", "sqlite:///./adk_sessions_chapter15.db")

if GOOGLE_CLOUD_PROJECT and GCS_BUCKET_NAME and DATABASE_URL:
    try:
        db_session_svc = DatabaseSessionService(db_url=DATABASE_URL)
        gcs_artifact_svc = GcsArtifactService(bucket_name=GCS_BUCKET_NAME, project=GOOGLE_CLOUD_PROJECT)
        # memory_svc_persistent = VertexAiRagMemoryService(...) # Or other persistent memory

        runner_persistent = Runner(
            app_name="MyPersistentApp",
            agent=my_root_agent,
            session_service=db_session_svc,
            artifact_service=gcs_artifact_svc,
            # memory_service=memory_svc_persistent
            memory_service=InMemoryMemoryService() # Placeholder for simplicity
        )
        print(f"Runner initialized with persistent services for app: {runner_persistent.app_name}")
    except Exception as e:
        print(f"Could not initialize persistent Runner: {e}")
        print("Ensure Database, GCS bucket, and relevant SDKs/permissions are set up.")
else:
    print("Skipping persistent Runner setup due to missing env vars (GOOGLE_CLOUD_PROJECT, ADK_ARTIFACT_GCS_BUCKET, ADK_DATABASE_URL).")
