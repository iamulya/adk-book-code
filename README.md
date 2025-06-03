# Building Intelligent Agents with Google ADK - Code Examples

This repository contains the companion code examples for the book "Building Intelligent Agents using Google's Agent Development Kit (ADK)". Each chapter's code is organized into its respective directory.

## Prerequisites

*   **Python**: Version 3.12 or higher (as specified in `pyproject.toml`).
*   **`uv`**: This project uses `uv` for package management. If you don't have it, install it via pip: `pip install uv`.
*   **API Keys & Credentials**:
    *   By default, Gemini models are used for the code examples. If you would rather use another model, please change the DEFAULT_LLM and DEFAULT_REASONING_LLM in `src/building_intelligent_agents/utils.py`.
    *   Google Cloud Project: Required for examples using Vertex AI (including Claude on Vertex, Vertex AI Code Executor, Vertex AI RAG Memory) and Google Cloud services like Application Integration, Secret Manager.
    *   OpenAI API Key: For examples using OpenAI models via LiteLLM (Chapter 10).
    *   Serper API Key: For the CrewAI SerperDevTool example (Chapter 8).
    *   Google OAuth 2.0 Client ID & Secret: For examples using Google API tools like Google Calendar (Chapter 7).
    *   Specific credentials for other services like Spotify (Chapter 7) or custom API Hub setups as detailed in respective chapter examples.
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
    *   Add the necessary credentials. See the example below:

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
    ADK_GOOGLE_OAUTH_CLIENT_ID="YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com"
    ADK_GOOGLE_OAUTH_CLIENT_SECRET="YOUR_GOOGLE_OAUTH_CLIENT_SECRET"

    # --- Optional/Specific Example Variables (Refer to chapter code for exact needs) ---

    # For Chapter 7: API Hub Example
    # MY_APIHUB_API_RESOURCE_NAME="projects/your-gcp-project/locations/your-location/apis/your-api-id"

    # For Chapter 7: Spotify Example (obtain a Bearer token manually)
    # SPOTIFY_BEARER_TOKEN="Bearer YOUR_SPOTIFY_ACCESS_TOKEN_OBTAINED_VIA_CLIENT_CREDENTIALS_FLOW"

    # For Chapter 8: Application Integration Example
    # APP_INTEGRATION_LOCATION="your-app-integration-region" # e.g., us-central1
    # MY_APP_INTEGRATION_NAME="your-app-integration-name"
    # MY_APP_INTEGRATION_TRIGGER_ID="api_trigger/your-trigger-id"
    # APP_INTEGRATION_SA_KEY_PATH="/path/to/your/app-integration-sa-key.json" # Optional, can use Application Default Credentials

    # For Chapter 21: Tool Auth Config Example (Petstore dummy values, no real API calls)
    # MY_PETSTORE_OAUTH_CLIENT_ID="dummy_client_id_for_petstore_example"
    # MY_PETSTORE_OAUTH_CLIENT_SECRET="dummy_client_secret_for_petstore_example"
    # MY_PETSTORE_API_KEY="dummy_api_key_value_for_petstore_example"
    ```
    **Note**: The `src/building_intelligent_agents/utils.py` script loads the `.env` file from the root project directory (`adk-book-code`).

## Running the Examples

Most examples are designed to be run as Python modules from the root directory of the project (`adk-book-code/`) after installation. 

Now you can run any example by specifying the module path relative to the `building_intelligent_agents` package. The general command structure is:

```bash
python -m building_intelligent_agents.chapter<N>.path.to.module
```

For example, to run the main example from Chapter 1:
```bash
python -m building_intelligent_agents.chapter1.main
```

To run the calculator tool example from Chapter 5:
```bash
python -m building_intelligent_agents.chapter5.tools.calculator
```

**Important Notes on Running Examples**:
*   Ensure your virtual environment is activated.
*   Ensure your `.env` file is correctly configured with the necessary API keys and credentials for the specific example you are running.
*   Some examples, particularly those involving OAuth (like the Google Calendar tool in Chapter 7) or complex UI interactions, are best experienced using the ADK Dev UI. To use the Dev UI:
    1.  Navigate to the chapter: for e.g. `cd src/building_intelligent_agents/chapter4`
    2.  Decide on the agent you want to test and update the `init.py` file in the chapter directory to include the agent you want to test: for e.g.
    2.  Run the ADK web server: `adk web .`
    3.  Open your browser to `http://localhost:8000` (or the port indicated).
    4.  Navigate to the agent definition file (e.g., `chapter7/tools_examples/calendar-agent/agent.py`) in the Dev UI to interact with it. The Dev UI will help manage the OAuth flow for Google API tools.

## Project Structure

The code is organized by book chapters:

```
adk-book-code/
├── pyproject.toml                # Project configuration and dependencies
├── src/
│   └── building_intelligent_agents/
│       ├── __init__.py
│       ├── utils.py                # Common utilities, env loading, LLM defaults
│       ├── chapter1/               # Examples for Chapter 1
│       │   └── ...
│       ├── chapter2/
│       │   └── ...
│       └── ...                     # Other chapters
└── .env                            # (User-created) For API keys and secrets
```

## Key Files

- `pyproject.toml`: Defines project metadata, dependencies, and build system configuration.
- `src/building_intelligent_agents/utils.py`: Contains utility functions for loading environment variables from `.env` and defines default LLM model names.
- `.env` (to be created by you): Stores sensitive information like API keys and project configurations.

## Specific Considerations

*   **OAuth for Google API Tools (e.g., Chapter 7 - Calendar)**: These tools require user authorization. The ADK Dev UI (`adk web .`) is the recommended way to test these examples as it handles the OAuth 2.0 redirect flow.
*   **API Key Requirements**: Many examples rely on external services. Ensure the relevant API keys (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, `SERPER_API_KEY`, Spotify tokens, etc.) are correctly set in your `.env` file.
*   **Cloud Services**: Examples using Vertex AI, Google Cloud Storage, Application Integration, etc., require a configured Google Cloud Project with the necessary APIs enabled and appropriate permissions for your credentials (user or service account).
*   **Unsafe Code Execution (Chapter 9)**: The `UnsafeLocalCodeExecutor` example will execute code directly in your local Python environment. **Use this with extreme caution and only in trusted development environments.** Never use it with untrusted LLM outputs or in production.
*   **Conceptual Examples**: Some files (e.g., in Chapters 15, 17, 18, 19, 20, 25) are more conceptual or provide setup snippets rather than fully runnable CLI examples due to dependencies on UI interactions, external systems not easily mockable, or extensive setup. These are best understood in conjunction with the book's text and tested via the ADK Dev UI where applicable.
*   **Docker and Node.js**: Ensure Docker is running for `ContainerCodeExecutor` examples (Chapter 9). Ensure Node.js and `npx` are installed and in your PATH for the `MCPToolset` filesystem server example (Chapter 8).

Happy building with Google ADK!