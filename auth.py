from google.oauth2 import service_account

def get_credentials():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=SCOPES
    )
    return creds
