
# auth_examples/service_account_tool_demo.py
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, ServiceAccount, ServiceAccountCredential
import os; import json
SA_KEY_FILE_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS"); SA_KEY_JSON_CONTENT = None
if SA_KEY_FILE_PATH and os.path.exists(SA_KEY_FILE_PATH):
    with open(SA_KEY_FILE_PATH, 'r') as f: SA_KEY_JSON_CONTENT = json.load(f) 
    print(f"Loaded service account key from: {SA_KEY_FILE_PATH}")
else: print(f"Warning: GOOGLE_APPLICATION_CREDENTIALS not set/found. Using use_default_credential=True.")
if SA_KEY_JSON_CONTENT:
    sa_credential_details = ServiceAccountCredential(**SA_KEY_JSON_CONTENT)
    service_account_config = ServiceAccount(service_account_credential=sa_credential_details, scopes=["https://www.googleapis.com/auth/cloud-platform"])
else: service_account_config = ServiceAccount(use_default_credential=True, scopes=["https://www.googleapis.com/auth/cloud-platform"])
service_account_auth_cred = AuthCredential(auth_type=AuthCredentialTypes.SERVICE_ACCOUNT, service_account=service_account_config)
print(f"\nConceptual Service Account AuthCredential prepared (type: {service_account_auth_cred.auth_type}).")

