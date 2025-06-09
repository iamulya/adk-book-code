# Building Intelligent Agents with Google ADK - Code Examples

This repository contains the companion code examples for the book "Building Intelligent Agents using Google's Agent Development Kit (ADK)". Each chapter's code is organized into its respective directory.

## Project Structure

```
adk-book-code/
├── .devcontainer/                # Dev Container & Codespaces configuration
├── pyproject.toml                # Project configuration and dependencies
├── uv.lock                       # Pinned dependencies for reproducible builds
├── src/
│   └── building_intelligent_agents/
│       ├── __init__.py
│       ├── utils.py                # Common utilities, env loading, LLM defaults
│       ├── chapter1/
│       │   └── __init__.py         # (Un)comment agents to test in Dev UI
│       └── ...                     # Other chapters
└── .env.example                    # Example environment file
└── .env                            # (User-created) For API keys and secrets
```

## Setup Instructions

You can set up your development environment in one of three ways. Using a container-based approach (Codespaces or Local Dev Container) is highly recommended for a quick and consistent setup.

### Option 1: Using GitHub Codespaces (Easiest)

This method runs a fully configured development environment in the cloud, accessible through your browser. It's the fastest way to get started.

**Prerequisites:**
*   A GitHub account.

**Steps:**

1.  Click the **`< > Code`** button.
2.  Go to the **Codespaces** tab.
3.  Click **"Create codespace on main"** (or your current branch). GitHub will prepare the environment based on the `.devcontainer/devcontainer.json` configuration, which may take a few minutes.
4.  Once the Codespace is ready, it will open in a browser-based VS Code editor. The virtual environment should be automatically activated in the terminal. Proceed to the **[Environment Variable Configuration](#environment-variable-configuration-env-file)** step below.

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
3.  **Reopen in Container**: A notification will usually appear in the bottom-right corner asking if you want to "Reopen in Container". Click it. If not, open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`) and type "Dev Containers: Rebuild and Reopen in Container" or "Dev Containers: Reopen in Container". VS Code will build the container based on the `.devcontainer/devcontainer.json` configuration.
4.  Once the container is running, the virtual environment should be automatically activated in the terminal. Proceed to the **[Environment Variable Configuration](#environment-variable-configuration-env-file)** step below.

> [!IMPORTANT]  
> ## For Option 1 and Option 2 users
> When the setup is done for the *first time*, it might not have the Python virtual environment activated in the terminal open by default. Simply open a new terminal - there you should have the virtual environment automatically activated, verifiable by the presence of `(adk-book-code)` in your prompt. 

### Option 3: Manual Local Setup

Follow these steps if you prefer to configure your local machine manually.

#### Prerequisites

*   **Python**: Version 3.12 or higher.
*   **`uv`**: This project uses `uv` for package management. Install it if you haven't: `pip install uv` (or see official `uv` installation).
*   **Docker**: Required for containerized code execution examples (Chapter 9). Ensure Docker Desktop (or Docker Engine) is installed and running.
*   **Node.js & npx**: Required for the MCP Filesystem server example (Chapter 8).

#### Steps

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
    This project uses `uv.lock` for reproducible builds.
    ```bash
    uv pip sync uv.lock
    uv pip install --no-deps -e . # Install current project in editable mode
    ```
4.  Proceed to the **[Environment Variable Configuration](#environment-variable-configuration-env-file)** step below.

## Environment Variable Configuration (`.env` file)

Regardless of which setup option you choose, you must configure your secrets and API keys. These are managed through a `.env` file in the project's root directory (`adk-book-code/.env`).

**Note for Codespaces/Dev Containers Users:** If you are using Option 1 or 2, you should **not** commit your actual `.env` file with secrets. Instead, configure these as **Codespaces Secrets** (Repository Settings > Secrets and variables > Codespaces > New repository secret). The `devcontainer.json` is set up to make these available as environment variables inside the container. For local dev container usage *without* Codespaces secrets, you can create a local `.env` file which will be used if present. Check out the `.env.example` file to find all of the environment variables used in the code.

**Note on Required Keys:** It is not necessary to enter values for all keys mentioned in the `.env.example` file. However, you **must** provide an API key for the LLM you intend to use. By default, examples use Google Gemini.
*   For **Gemini models via Google AI Studio (Recommended for easy start)**: Set `GOOGLE_API_KEY`.
    The easiest way to get an API key for Google's Gemini models is through Google AI Studio:

        1.  Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) (Google AI Studio).
        2.  You might need to sign in with your Google account.
        3.  Click on "**Create API key**".
        4.  A new API key will be generated. Copy this key.
        5.  Paste this key as the value for `GOOGLE_API_KEY` in your `.env` file.
            ```env
            GOOGLE_API_KEY="YOUR_COPIED_GEMINI_API_KEY"
            ```
    **Important:** Keep this API key secure and do not commit it to your repository.
*   For **OpenAI models via LiteLLM**: Set `OPENAI_API_KEY`.
*   For **other LLMs via LiteLLM**: Consult the [LiteLLM documentation](https://docs.litellm.ai/docs/providers) for the correct environment variable for your chosen model and key.
*   If you are having trouble, check out the "Use your favorite LLM" chapter in the book for further support.

**Steps to Configure:**

1.  **Create the `.env` file**: In the project's root directory (`adk-book-code/`), copy the example file:
    ```bash
    cp .env.example .env
    ```
2.  **Edit the `.env` file** with your actual credentials. See `.env.example` below for structure.

**.env.example (for reference, populate your actual `.env` file)**:
```env
# Google Gemini API Key (obtained from Google AI Studio - see instructions above)
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
# If using Vertex AI for Gemini instead of AI Studio, you might not need GOOGLE_API_KEY,
# but GOOGLE_CLOUD_PROJECT and authentication (e.g. gcloud auth application-default login) are needed.
# GOOGLE_GENAI_USE_VERTEXAI=0 # Set to 1 to default to Vertex AI for Gemini (requires GOOGLE_CLOUD_PROJECT)

# Google Cloud Project details (for Vertex AI, Claude on Vertex, App Integration, etc.)
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="your-gcp-region" # e.g., us-central1

# Path to your Google Cloud service account key JSON file (for some GCP services like Chapter 21)
# GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

# OpenAI API Key (for LiteLLM OpenAI examples - Chapter 10)
OPENAI_API_KEY="sk-YOUR_OPENAI_API_KEY"

# Serper API Key (for CrewAI SerperDevTool example - Chapter 8)
SERPER_API_KEY="YOUR_SERPER_API_KEY"

# For Chapter 7: Spotify Example (obtain a Bearer token manually via Client Credentials Flow)
SPOTIFY_BEARER_TOKEN="Bearer YOUR_SPOTIFY_ACCESS_TOKEN_OBTAINED_VIA_CLIENT_CREDENTIALS_FLOW"

# Google OAuth Credentials for ADK (e.g., for Calendar tool - Chapter 7)
# The redirect URI for local ADK Dev UI usage is typically: http://localhost:8008/oauth_callback
CALENDAR_OAUTH_CLIENT_ID="YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com"
CALENDAR_OAUTH_CLIENT_SECRET="YOUR_GOOGLE_OAUTH_CLIENT_SECRET"

# For Chapter 7: Spotify Example (obtain a Bearer token manually via Client Credentials Flow)
SPOTIFY_BEARER_TOKEN="Bearer YOUR_SPOTIFY_ACCESS_TOKEN"

# --- Optional/Specific Example Variables (Refer to chapter code for exact needs) ---
# VERTEX_AI_SEARCH_DATA_STORE_ID="projects/<PROJECT_ID>/locations/<LOCATION>/collections/default_collection/dataStores/<DATA_STORE_ID>"
# MY_APIHUB_API_RESOURCE_NAME="projects/your-gcp-project/locations/your-location/apis/your-api-id"
# APP_INTEGRATION_LOCATION="your-app-integration-region"
# MY_APP_INTEGRATION_NAME="your-app-integration-name"
# MY_APP_INTEGRATION_TRIGGER_ID="api_trigger/your-trigger-id"
# MY_SELF_HOSTED_LLM_API_BASE="http://localhost:8000/v1" # Example for LiteLLM custom endpoint
# ADK_ARTIFACT_GCS_BUCKET="your-adk-artifacts-bucket-name"
# ADK_RAG_CORPUS_ID="your-rag-corpus-id-or-full-resource-name"
# ADK_DATABASE_URL="sqlite:///./adk_sessions.db" # Example for persistent session storage
```
**Note**: The `src/building_intelligent_agents/utils.py` script loads this `.env` file from the project root. In a Codespace with secrets defined, `os.getenv()` will pick up the Codespaces secrets first.

## Running the Examples

Once your environment is set up (manually or via a container) and your `.env` file (or Codespaces secrets) are configured:

1.  **Ensure your virtual environment is activated** (if using manual setup or if not auto-activated in container).
    In Codespaces/Dev Container, the virtual environment should already be activated if setup was successful. Look for `(adk-book-code)` in your prompt. If it is not there, start a new terminal. If that also doesn't work, activate the virtual environment manually by running `source .venv/bin/activate` on Linux/macOS or `.venv\Scripts\activate` on Windows.

2.  **Navigate to the `src/building_intelligent_agents` directory**:
    ```bash
    # If you are in adk-book-code root:
    cd src/building_intelligent_agents
    ```
    *All `python -m` and `adk web .` commands below assume you are in this directory.*

3.  **Run an example script via `python -m`**:
    To run any example directly from the command line:
    ```bash
    python -m chapter<N>.path.to.module
    ```
    For example, to run the simple assistant from Chapter 1:
    ```bash
    python -m chapter1.simple_assistant
    ```

4.  **Run an example using the ADK Dev UI (`adk web .`)**:
    The Dev UI is ideal for examples involving OAuth or for viewing detailed execution traces.
    1.  **Ensure you are in the `src/building_intelligent_agents` directory.**
    2.  **Configure `__init__.py` for the desired agent**: Each chapter's `__init__.py` file (e.g., `src/building_intelligent_agents/chapter7/__init__.py`) contains commented-out import lines. **Uncomment the line corresponding to the agent you want to test** in that chapter's `__init__.py`, making it the `root_agent`. For example, to test the Calendar agent, edit `src/building_intelligent_agents/chapter7/__init__.py` and ensure the line `from .calendar_agent import calendar_agent as root_agent` is active and others are commented out.
    3.  Run the ADK web server from the `src/building_intelligent_agents` directory:
        ```bash
        adk web .
        ```
    4.  Open your browser to the URL provided (usually `http://localhost:8000`). If you are in a Codespace, VS Code will typically offer to forward the port automatically, and you can open it in your local browser.
    5.  In the Dev UI, select the chapter folder (e.g., `chapter7`) from the agent selector on the top-left. You can then interact with the agent defined as `root_agent` for that chapter.

Happy building with Google ADK!