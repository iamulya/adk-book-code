import os
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner

def load_environment_variables():
    """
    Load environment variables from a .env file located in the parent directory of the current script.
    """
    # Ensure the .env file is loaded from the parent directory
    # Get the directory of the current script
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the .env file in the parent directory
    dotenv_path = os.path.join(current_script_dir, ".env")

    # Load the .env file if it exists
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Loaded environment variables from: {dotenv_path}")
    else:
        print(f"Warning: .env file not found at {dotenv_path}")

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