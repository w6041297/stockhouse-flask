from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class SheetWriter:
    def __init__(self, json_path, sheet_id):
        creds = service_account.Credentials.from_service_account_file(json_path, scopes=SCOPES)
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet_id = sheet_id

    def append(self, sheet_name, row_values):
        body = {
            "values": [row_values]
        }
        result = self.service.spreadsheets().values().append(
            spreadsheetId=self.sheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        return result