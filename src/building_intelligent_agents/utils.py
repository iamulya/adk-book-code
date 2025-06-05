import os
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner

DEFAULT_LLM="gemini-2.0-flash"#"gemini-2.5-flash-preview-05-20"
DEFAULT_REASONING_LLM="gemini-2.5-flash-preview-05-20"

def load_environment_variables():
    """
    Load environment variables from a .env file located in the project root directory.
    Assumes utils.py is in src/your_package_name/
    """
    # Get the directory of the current script (utils.py)
    # e.g., /path/to/project/src/building_intelligent_agents
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    # Go up one level to the 'src' directory
    # e.g., /path/to/project/src
    src_dir = os.path.dirname(current_script_dir)

    # Go up one more level to the project root directory
    # e.g., /path/to/project
    project_root = os.path.dirname(src_dir)

    # Construct the path to the .env file in the project root
    dotenv_path = os.path.join(project_root, ".env")

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Loaded environment variables from: {dotenv_path}")
    else:
        print(f"Warning: .env file not found at {dotenv_path}. Ensure it's in the project root.")

def create_session(runner: InMemoryRunner, session_id: str, user_id: str, state=None):
    """
    Create a new session using the provided runner.
    
    :param runner: The InMemoryRunner instance to use for session creation.
    :param session_id: The ID of the session to create.
    :param user_id: The ID of the user for whom the session is created.
    """
    import asyncio
    print(f"Creating session: {session_id} for user: {user_id} on app: {runner.app_name}")
    
    try:
        asyncio.run(runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
            state=state or {}
        ))
        print("Session created successfully.")
    except Exception as e:
        print(f"Error creating session: {e}")
        exit()