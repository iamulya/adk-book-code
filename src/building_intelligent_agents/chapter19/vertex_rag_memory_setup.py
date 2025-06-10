from google.adk.memory import VertexAiRagMemoryService
import os

GCP_PROJECT_RAG = os.getenv("GOOGLE_CLOUD_PROJECT")
# Vertex AI RAG Corpus Name/ID or full resource name
# e.g., "my_adk_sessions_corpus" or
# "projects/<PROJECT_ID>/locations/<LOCATION>/ragCorpora/<CORPUS_ID>"
RAG_CORPUS_ID = os.getenv("ADK_RAG_CORPUS_ID")
# Optional location for the RAG corpus if not part of the full resource name
RAG_CORPUS_LOCATION = os.getenv("ADK_RAG_CORPUS_LOCATION", "us-central1")

if GCP_PROJECT_RAG and RAG_CORPUS_ID:
    try:
        # Construct the full corpus resource name if only ID is given
        full_rag_corpus_name = RAG_CORPUS_ID
        if not RAG_CORPUS_ID.startswith("projects/"):
            full_rag_corpus_name = f"projects/{GCP_PROJECT_RAG}/locations/{RAG_CORPUS_LOCATION}/ragCorpora/{RAG_CORPUS_ID}"

        rag_memory_service = VertexAiRagMemoryService(
            rag_corpus=full_rag_corpus_name,
            similarity_top_k=5, # Retrieve top 5 most similar chunks
            # vector_distance_threshold=0.7 # Optional: filter by similarity score
        )
        print(f"VertexAiRagMemoryService initialized with corpus: {full_rag_corpus_name}")

        # This instance can now be passed to a Runner
        # from google.adk.runners import Runner
        # my_agent_for_rag = ...
        # runner_with_rag_mem = Runner(
        #     app_name="MyRagApp", # This app_name is used in file display names in RAG
        #     agent=my_agent_for_rag,
        #     session_service=...,
        #     memory_service=rag_memory_service
        # )
    except ImportError:
        print("Vertex AI SDK with RAG support not found. Ensure 'google-cloud-aiplatform[rag]' is installed or similar.")
    except Exception as e:
        print(f"Failed to initialize VertexAiRagMemoryService: {e}")
        print("Ensure RAG Corpus exists, Vertex AI API is enabled, and auth is correct.")
else:
    print("GOOGLE_CLOUD_PROJECT or ADK_RAG_CORPUS_ID environment variables not set. Skipping VertexAiRagMemoryService setup.")