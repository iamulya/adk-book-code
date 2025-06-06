# auth_examples/service_account_tool_demo.py
from google.adk.tools.openapi_tool import RestApiTool # Conceptual
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, ServiceAccount, ServiceAccountCredential
from fastapi.openapi.models import HTTPBearer # For the scheme
import os
import json

# --- Conceptual Tool that uses Google Service Account Auth ---
# Assume this tool's OpenAPI spec defines a securityScheme like:
# "GoogleServiceAccountAuth": { "type": "http", "scheme": "bearer", "bearerFormat": "JWT" }
# And the operation uses this security scheme.

# conceptual_gcp_tool = RestApiTool(name="list_gcs_buckets", ...)
# conceptual_gcp_tool.auth_scheme = HTTPBearer(bearerFormat="JWT") # The scheme after exchange

# --- Configure Service Account Credential ---
SA_KEY_FILE_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # Standard env var for ADC
SA_KEY_JSON_CONTENT = None
if SA_KEY_FILE_PATH and os.path.exists(SA_KEY_FILE_PATH):
    with open(SA_KEY_FILE_PATH, 'r') as f:
        SA_KEY_JSON_CONTENT = json.load(f) # Load the dict
    print(f"Loaded service account key from: {SA_KEY_FILE_PATH}")
else:
    print(f"Warning: GOOGLE_APPLICATION_CREDENTIALS not set or file not found. Using use_default_credential=True (will only work in GCP env).")

if SA_KEY_JSON_CONTENT:
    sa_credential_details = ServiceAccountCredential(**SA_KEY_JSON_CONTENT)
    service_account_config = ServiceAccount(
        service_account_credential=sa_credential_details,
        scopes=["<https://www.googleapis.com/auth/cloud-platform>"] # Example scope
    )
else: # Fallback to Application Default Credentials
    service_account_config = ServiceAccount(
        use_default_credential=True,
        scopes=["<https://www.googleapis.com/auth/cloud-platform>"]
    )

service_account_auth_cred = AuthCredential(
    auth_type=AuthCredentialTypes.SERVICE_ACCOUNT,
    service_account=service_account_config
)

# conceptual_gcp_tool.configure_auth_credential(service_account_auth_cred)
print(f"\nConceptual Service Account AuthCredential prepared (type: {service_account_auth_cred.auth_type}).")

# When conceptual_gcp_tool.run_async() is called:
# 1. ToolAuthHandler sees auth_scheme (HTTPBearer) and auth_credential (SERVICE_ACCOUNT type).
# 2. AutoAuthCredentialExchanger picks ServiceAccountCredentialExchanger.
# 3. ServiceAccountCredentialExchanger uses SA key or ADC to get an access token.
# 4. Returns new AuthCredential(auth_type=HTTP, http=HttpAuth(scheme="bearer", token=...))
# 5. RestApiTool uses this Bearer token.