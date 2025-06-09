# Building Intelligent Agents with Google ADK - Code Examples

This repository contains the companion code examples for the book "Building Intelligent Agents using Google's Agent Development Kit (ADK)". Each chapter's code is organized into its respective directory.

## Project Structure

```
adk-book-code/
├── .devcontainer/                # Dev Container & Codespaces configuration
├── pyproject.toml                # Project configuration and dependencies
├── src/
│   └── building_intelligent_agents/
│       ├── __init__.py
│       ├── utils.py                # Common utilities, env loading, LLM defaults
│       ├── chapter1/
│       │   └── __init__.py         # (Un)comment agents to test in Dev UI
│       └── ...                     # Other chapters
└── .env                            # (User-created) For API keys and secrets
```

## Prerequisites

*   **Python**: Version 3.12 or higher.
*   **`uv`**: This project uses `uv` for package management. 
*   **API Keys & Credentials**: You will need to configure API keys and credentials in a `.env` file as described in the setup instructions.
*   **Docker**: Required for containerized code execution examples (Chapter 9) and for using the Local Dev Container setup option. Ensure Docker Desktop (or Docker Engine) is installed and running.
*   **Node.js & npx**: Required for the MCP Filesystem server example (Chapter 8).

## Setup Instructions

You can set up your development environment in one of three ways. Using a container-based approach (Codespaces or Local Dev Container) is highly recommended for a quick and consistent setup.

### Option 1: Using GitHub Codespaces (Easiest)

This method runs a fully configured development environment in the cloud, accessible through your browser. It's the fastest way to get started.

**Prerequisites:**
*   A GitHub account.

**Steps:**
1.  Navigate to the main page of this repository on GitHub.
2.  Click the **`< > Code`** button.
3.  Go to the **Codespaces** tab.
4.  Click **"Create codespace on main"**. GitHub will prepare the environment for you, which may take a few minutes.
5.  Once the Codespace is ready, it will open in a browser-based VS Code editor. Proceed to the **[Environment Variable Configuration](#environment-variable-configuration-env-file)** step below.

### Option 2: Using a Local Dev Container

This method uses VS Code and Docker on your local machine to create the same consistent environment as Codespaces.

**Prerequisites:**
*   Visual Studio Code
*   The [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code.
*   Docker Desktop installed and running.

**Steps:**
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/iamulya/adk-book-code.git
    cd adk-book-code
    ```
2.  **Open in VS Code**: Open the cloned `adk-book-code` folder in VS Code.
3.  **Reopen in Container**: A notification will appear in the bottom-right corner asking if you want to "Reopen in Container". Click it. VS Code will build the container based on the `.devcontainer/devcontainer.json` configuration.
4.  Once the container is running, proceed to the **[Environment Variable Configuration](#environment-variable-configuration-env-file)** step below.

### Option 3: Manual Local Setup

Follow these steps if you prefer to configure your local machine manually.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/iamulya/adk-book-code.git
    cd adk-book-code
    ```
2.  **Create a Virtual Environment**:
    Using `uv`:
    ```bash
    uv venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate  # On Windows
    ```
3.  **Install Dependencies**:
    Using `uv`:
    ```bash
    uv pip sync uv.lock
    uv pip install -e .
    ```
4.  Proceed to the **[Environment Variable Configuration](#environment-variable-configuration-env-file)** step below.

## Environment Variable Configuration (`.env` file)

Regardless of which setup option you choose, you must configure your secrets and API keys in a `.env` file.

**Note** - It is not necessary to enter values for all of the keys mentioned in the .env file. However, you **must** enter your API key for the LLM you will be using, i.e. GOOGLE_API_KEY if using Gemini, OPENAI_API_KEY if using GPT Models or the api key of your favorite LLM model (You might need to consult [LiteLLM docs](https://docs.litellm.ai/docs/providers) to make sure you set the correct environment variable for your LLM key). If you are having trouble using your LLM, check out "Use your favorite LLM" chapter in the book for further instructions.

1.  **Create the `.env` file** in the project's root directory (`adk-book-code/.env`). If you are in a Dev Container or Codespace, you can do this from the terminal:
    ```bash
    cp .env.example .env
    ```
2.  **Edit the `.env` file** with your actual credentials.

**.env.example**:
```env
# Google Gemini API Key (for direct Gemini use without Vertex AI etc.)  OR your favorite LLM API Key
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"

# Google Cloud Project details (for Vertex AI, Claude on Vertex, App Integration, etc.)
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="your-gcp-region" # e.g., us-central1

# Path to your Google Cloud service account key JSON file (for some GCP services like Chapter 21)
# GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

# OpenAI API Key (for LiteLLM OpenAI examples - Chapter 10)
OPENAI_API_KEY="sk-YOUR_OPENAI_API_KEY"

# Serper API Key (for CrewAI SerperDevTool example - Chapter 8)
SERPER_API_KEY="YOUR_SERPER_API_KEY"

# Google OAuth Credentials for ADK (e.g., for Calendar tool - Chapter 7)
# The redirect URI for local ADK Dev UI usage is typically: http://localhost:8008/oauth_callback
CALENDAR_OAUTH_CLIENT_ID="YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com"
CALENDAR_OAUTH_CLIENT_SECRET="YOUR_GOOGLE_OAUTH_CLIENT_SECRET"

# For Chapter 7: Spotify Example (obtain a Bearer token manually via Client Credentials Flow)
SPOTIFY_BEARER_TOKEN="Bearer YOUR_SPOTIFY_ACCESS_TOKEN_OBTAINED_VIA_CLIENT_CREDENTIALS_FLOW"

# --- Optional/Specific Example Variables (Refer to chapter code for exact needs) ---
# VERTEX_AI_SEARCH_DATA_STORE_ID="projects/<PROJECT_ID>/locations/<LOCATION>/collections/default_collection/dataStores/<DATA_STORE_ID>"
# MY_APIHUB_API_RESOURCE_NAME="projects/your-gcp-project/locations/your-location/apis/your-api-id"
# APP_INTEGRATION_LOCATION="your-app-integration-region"
# MY_APP_INTEGRATION_NAME="your-app-integration-name"
# MY_APP_INTEGRATION_TRIGGER_ID="api_trigger/your-trigger-id"
# MY_SELF_HOSTED_LLM_API_BASE="http://localhost:8000/v1"
# ADK_ARTIFACT_GCS_BUCKET="your-adk-artifacts-bucket-name"
# ADK_RAG_CORPUS_ID="your-rag-corpus-id-or-full-resource-name"
# ADK_DATABASE_URL="sqlite:///./adk_sessions.db"
```
**Note**: The `src/building_intelligent_agents/utils.py` script loads this `.env` file from the project root.

## Running the Examples

Once your environment is set up (manually or via a container), you can run the examples.

1.  **Navigate to the `src/building_intelligent_agents` directory**:
    ```bash
    cd src/building_intelligent_agents
    ```

2.  **Run an example script via `python -m`**:
    To run any example directly from the command line:
    ```bash
    python -m chapter<N>.path.to.module
    ```
    For example, to run the simple assistant from Chapter 1:
    ```bash
    python -m chapter1.simple_assistant
    ```

3.  **Run an example using the ADK Dev UI (`adk web .`)**:
    The Dev UI is ideal for examples involving OAuth or for viewing detailed execution traces.
    1.  **Ensure you are in the `src/building_intelligent_agents` directory.**
    2.  **Configure `__init__.py` for the desired agent**: Each chapter's `__init__.py` file contains commented-out import lines. **Uncomment the line corresponding to the agent you want to test** in the `__init__.py` file within that *specific chapter's directory*. For example, to test the Calendar agent, edit `src/building_intelligent_agents/chapter7/__init__.py` and uncomment `from .calendar_agent import calendar_agent as root_agent`.
    3.  Run the ADK web server from the `src/building_intelligent_agents` directory:
        ```bash
        adk web .
        ```
    4.  Open your browser to the URL provided (usually `http://localhost:8000`). If you are in a Codespace, VS Code will automatically forward the port.
    5.  In the Dev UI, select the chapter folder (e.g., `chapter7`) from the file explorer on the left. You can then interact with the agent defined as `root_agent` for that chapter.

Happy building with Google ADK!
