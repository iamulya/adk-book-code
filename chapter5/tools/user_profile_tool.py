
# tools/user_profile_tool.py
from google.adk.tools import FunctionTool
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List as PyList
class UserProfile(BaseModel):
    username: str; email: EmailStr; age: Optional[int] = None; interests: PyList[str] = []
def update_user_profile(profile: UserProfile) -> dict:
    """Updates a user's profile information. Args: profile: A UserProfile object..."""
    print(f"Updating profile for {profile.username} with email {profile.email}")
    return {"status": "success", "updated_username": profile.username}
user_profile_updater_tool = FunctionTool(func=update_user_profile)

