import os
from dotenv import load_dotenv

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