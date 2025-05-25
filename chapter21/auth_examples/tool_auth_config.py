
# auth_examples/tool_auth_config.py
from google.adk.tools.openapi_tool import RestApiTool, OpenAPIToolset
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.auth.auth_schemes import AuthSchemeType 
from fastapi.openapi.models import APIKey, APIKeyIn, OAuth2, OAuthFlows, OAuthFlowImplicit 
import os
OAUTH_CLIENT_ID = os.getenv("MY_PETSTORE_OAUTH_CLIENT_ID", "dummy_client_id")
OAUTH_CLIENT_SECRET = os.getenv("MY_PETSTORE_OAUTH_CLIENT_SECRET", "dummy_client_secret") 
oauth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2, 
    oauth2=OAuth2Auth(client_id=OAUTH_CLIENT_ID, client_secret=OAUTH_CLIENT_SECRET)
)
print(f"Conceptual OAuth credential prepared: {oauth_credential.model_dump_json(indent=2, exclude_none=True)}")
MY_API_KEY_VALUE = os.getenv("MY_PETSTORE_API_KEY", "dummy_api_key_value")
api_key_credential_for_tool = AuthCredential(auth_type=AuthCredentialTypes.API_KEY, api_key=MY_API_KEY_VALUE)
print(f"\nConceptual API Key credential prepared: {api_key_credential_for_tool.model_dump_json(indent=2, exclude_none=True)}")

