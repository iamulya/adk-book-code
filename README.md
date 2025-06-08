# Building Intelligent Agents with Google ADK - Code Examples

This repository contains the companion code examples for the book "Building Intelligent Agents using Google's Agent Development Kit (ADK)". Each chapter's code is organized into its respective directory.

## Prerequisites

*   **Python**: Version 3.12 or higher (as specified in `pyproject.toml`).
*   **`uv`**: This project uses `uv` for package management. If you don't have it, install it via pip: `pip install uv`.
*   **API Keys & Credentials**:
    *   By default, Gemini models are used for the code examples. If you would rather use another model, please change the DEFAULT_LLM and DEFAULT_REASONING_LLM in `src/building_intelligent_agents/utils.py`.
    *   **Google Cloud Project**: Required for examples using Vertex AI (including Claude on Vertex, Vertex AI Code Executor, Vertex AI RAG Memory, Vertex AI Search) and Google Cloud services like Application Integration, Secret Manager. You will need to set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`.
    *   **OpenAI API Key**: For examples using OpenAI models via LiteLLM (Chapter 10). Set `OPENAI_API_KEY`.
    *   **Serper API Key**: For the CrewAI SerperDevTool example (Chapter 8). Set `SERPER_API_KEY`.
    *   **Google OAuth 2.0 Client ID & Secret**: For examples using Google API tools like Google Calendar (Chapter 7). Obtain from Google Cloud Console -> APIs & Services -> Credentials -> OAuth 2.0 Client IDs. Ensure your OAuth consent screen is configured and you've added necessary scopes. The redirect URI for local ADK Dev UI usage is typically: `http://localhost:8008/oauth_callback`. Set `CALENDAR_OAUTH_CLIENT_ID` and `CALENDAR_OAUTH_CLIENT_SECRET`.
    *   **Spotify API Bearer Token**: For the Spotify example (Chapter 7). You'll need to manually obtain a Bearer token via the Client Credentials Flow and set `SPOTIFY_BEARER_TOKEN`.
    *   Specific credentials for other services like custom API Hub setups or self-hosted LLMs as detailed in respective chapter examples.
*   **Docker**: Required for containerized code execution examples (Chapter 9, e.g., `container_executor_agent.py`). Ensure Docker Desktop (or Docker Engine) is installed and running.
*   **Node.js & npx**: Required for the MCP Filesystem server example (Chapter 8, `mcp_filesystem_agent.py`).

## Setup Instructions

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/iamulya/adk-book-code.git
    cd adk-book-code
    ```

2.  **Create a Virtual Environment (Recommended)**:
    Using `uv`:
    ```bash
    uv venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate  # On Windows
    ```
    Or using standard `venv`:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies**:
    Using `uv` (which will read `pyproject.toml`):
    ```bash
    uv pip install -e .
    ```
    The `-e .` installs the project in editable mode, making the `building_intelligent_agents` package (as defined in `pyproject.toml`) available.

4.  **Configure Environment Variables**:
    The project uses a `.env` file to manage API keys and other configurations.
    *   Create a `.env` file in the root of the project (`adk-book-code/.env`).
    *   Add the necessary credentials. See the example below and populate with your actual keys and IDs:

    **.env.example**:
    ```env
    # Google Gemini API Key (for direct Gemini use without Vertex AI etc.)  OR your favorite LLM API Key
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"

    # Google Cloud Project details (for Vertex AI, Claude on Vertex, App Integration, etc.)
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="your-gcp-region" # e.g., us-central1

    # Path to your Google Cloud service account key JSON file (for some GCP services like Chapter 21)
    # Ensure this service account has necessary permissions for the services you intend to use.
    # GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

    # OpenAI API Key (for LiteLLM OpenAI examples - Chapter 10)
    OPENAI_API_KEY="sk-YOUR_OPENAI_API_KEY"

    # Serper API Key (for CrewAI SerperDevTool example - Chapter 8)
    SERPER_API_KEY="YOUR_SERPER_API_KEY"

    # Google OAuth Credentials for ADK (e.g., for Calendar tool - Chapter 7)
    # Obtain from Google Cloud Console -> APIs & Services -> Credentials -> OAuth 2.0 Client IDs
    # Ensure your OAuth consent screen is configured and you've added necessary scopes.
    # The redirect URI for local ADK Dev UI usage is typically: http://localhost:8008/oauth_callback
    CALENDAR_OAUTH_CLIENT_ID="YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com"
    CALENDAR_OAUTH_CLIENT_SECRET="YOUR_GOOGLE_OAUTH_CLIENT_SECRET"

    # For Chapter 7: Spotify Example (obtain a Bearer token manually via Client Credentials Flow)
    # curl -X "POST" -H "Authorization: Basic <BASE64_ENCODED_CLIENT_ID:CLIENT_SECRET>" -d grant_type=client_credentials https://accounts.spotify.com/api/token
    SPOTIFY_BEARER_TOKEN="Bearer YOUR_SPOTIFY_ACCESS_TOKEN_OBTAINED_VIA_CLIENT_CREDENTIALS_FLOW"

    # --- Optional/Specific Example Variables (Refer to chapter code for exact needs) ---

    # For Chapter 6: Vertex AI Search Tool (LLM Knowledge Agent)
    # VERTEX_AI_SEARCH_DATA_STORE_ID="projects/<PROJECT_ID>/locations/<LOCATION>/collections/default_collection/dataStores/<DATA_STORE_ID>"

    # For Chapter 7: API Hub Example
    # MY_APIHUB_API_RESOURCE_NAME="projects/your-gcp-project/locations/your-location/apis/your-api-id"

    # For Chapter 8: Application Integration Example
    # APP_INTEGRATION_LOCATION="your-app-integration-region" # e.g., us-central1
    # MY_APP_INTEGRATION_NAME="your-app-integration-name"
    # MY_APP_INTEGRATION_TRIGGER_ID="api_trigger/your-trigger-id"
    # APP_INTEGRATION_SA_KEY_PATH="/path/to/your/app-integration-sa-key.json" # Optional, can use Application Default Credentials

    # For Chapter 10: LiteLLM Self-Hosted Example
    # MY_SELF_HOSTED_LLM_API_BASE="http://localhost:8000/v1"
    # MY_SELF_HOSTED_LLM_MODEL_NAME="custom/my-model" # e.g., "llama3" for Ollama, or a TGI model name

    # For Chapter 17: Google Cloud Storage Artifact Service
    # ADK_ARTIFACT_GCS_BUCKET="your-adk-artifacts-bucket-name"

    # For Chapter 18: Vertex AI RAG Memory Service
    # ADK_RAG_CORPUS_ID="your-rag-corpus-id-or-full-resource-name"
    # ADK_RAG_CORPUS_LOCATION="your-rag-corpus-location" # e.g., us-central1

    # For Chapter 15: DatabaseSessionService (if not using InMemory)
    # ADK_DATABASE_URL="sqlite:///./adk_sessions.db" # Example SQLite, or "mysql+pymysql://user:pass@host/db"
    ```
    **Note**: The `src/building_intelligent_agents/utils.py` script loads the `.env` file from the root project directory (`adk-book-code`).

## Running the Examples

All examples should be run from the `src/building_intelligent_agents` directory.

1.  **Navigate to the `src/building_intelligent_agents` directory**:
    ```bash
    cd src/building_intelligent_agents
    ```

2.  **Run an example script via `python -m`**:
    Once in `src/building_intelligent_agents`, you can run any example by specifying its module path. The general command structure is:
    ```bash
    python -m chapter<N>.path.to.module
    ```
    For example, to run the simple assistant from Chapter 1:
    ```bash
    python -m chapter1.simple_assistant
    ```
    To run the calculator tool example from Chapter 5:
    ```bash
    python -m chapter5.calculator
    ```

3.  **Run an example using the ADK Dev UI (`adk web .`)**:
    Some examples, particularly those involving OAuth (like the Google Calendar tool in Chapter 7) or complex UI interactions, are best experienced using the ADK Dev UI. To use the Dev UI:
    1.  **Ensure you are in the `src/building_intelligent_agents` directory.**
    2.  **Configure `__init__.py` for the desired agent**: The Dev UI needs to know which agent to load as the `root_agent`. Each chapter's `__init__.py` file contains commented-out lines like `#from .some_agent_file import some_agent as root_agent`. **Uncomment the line corresponding to the agent you want to test** in the `__init__.py` file within that *specific chapter's directory*. For example, to test the Calendar agent, you would edit `src/building_intelligent_agents/chapter7/__init__.py` and uncomment `from .calendar_agent import calendar_agent as root_agent`.
    3.  Run the ADK web server from the `src/building_intelligent_agents` directory:
        ```bash
        adk web .
        ```
    4.  Open your browser to `http://localhost:8000` (or the port indicated in the terminal).
    5.  In the Dev UI, you will see the project structure. **Navigate to the specific chapter (e.g., `chapter7`) and then to the agent definition file** (e.g., `calendar_agent.py`) to interact with it. The Dev UI will automatically load the `root_agent` you configured in the chapter's `__init__.py` and help manage OAuth flows and provide detailed execution traces.

**Important Notes on Running Examples**:
*   Ensure your virtual environment is activated.
*   Ensure your `.env` file (located in the top-level `adk-book-code` directory) is correctly configured with the necessary API keys and credentials for the specific example you are running.
*   **API Key Requirements**: Many examples rely on external services. Ensure the relevant API keys (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, `SERPER_API_KEY`, `SPOTIFY_BEARER_TOKEN`, `CALENDAR_OAUTH_CLIENT_ID`, `CALENDAR_OAUTH_CLIENT_SECRET`, etc.) are correctly set in your `.env` file.
*   **Cloud Services**: Examples using Vertex AI, Google Cloud Storage, Application Integration, etc., require a configured Google Cloud Project with the necessary APIs enabled and appropriate permissions for your credentials (user or service account). Ensure `google-cloud-aiplatform` is installed (it's in `pyproject.toml`).
*   **Unsafe Code Execution (Chapter 9)**: The `UnsafeLocalCodeExecutor` example will execute code directly in your local Python environment. **Use this with extreme caution and only in trusted development environments.** Never use it with untrusted LLM outputs or in production.
*   **Conceptual Examples**: Some files (e.g., in Chapters 15, 17, 18, 19, 20) are more conceptual or provide setup snippets rather than fully runnable CLI examples due to dependencies on UI interactions, external systems not easily mockable, or extensive setup. These are best understood in conjunction with the book's text and tested via the ADK Dev UI where applicable.
*   **Docker and Node.js**: Ensure Docker is running for `ContainerCodeExecutor` examples (Chapter 9). Ensure Node.js and `npx` are installed and in your PATH for the `MCPToolset` filesystem server example (Chapter 8).

Happy building with Google ADK!