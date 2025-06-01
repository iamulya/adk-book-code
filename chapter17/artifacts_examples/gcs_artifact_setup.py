# artifacts_examples/gcs_artifact_setup.py
from google.adk.artifacts import GcsArtifactService
import os

GCS_BUCKET_NAME_FOR_ADK = os.getenv("ADK_ARTIFACT_GCS_BUCKET")

if GCS_BUCKET_NAME_FOR_ADK:
    try:
        gcs_artifact_service_instance = GcsArtifactService(
            bucket_name=GCS_BUCKET_NAME_FOR_ADK
        )
        print(f"GcsArtifactService initialized for bucket: {GCS_BUCKET_NAME_FOR_ADK}")

        # This instance can now be passed to a Runner:
        # from google.adk.runners import Runner
        # from google.adk.sessions import DatabaseSessionService # (Example)
        # my_agent = ...
        # db_url = "sqlite:///./my_gcs_app_sessions.db"
        # runner_with_gcs = Runner(
        #     app_name="MyGCSApp",
        #     agent=my_agent,
        #     session_service=DatabaseSessionService(db_url=db_url),
        #     artifact_service=gcs_artifact_service_instance
        # )
    except Exception as e:
        print(f"Failed to initialize GcsArtifactService: {e}")
        print("Ensure 'google-cloud-storage' is installed, GCS bucket exists, and auth is configured.")
else:
    print("ADK_ARTIFACT_GCS_BUCKET environment variable not set. Skipping GCS ArtifactService setup.")
