import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

class DriveUploader:
    def __init__(self, json_path):
        creds = service_account.Credentials.from_service_account_file(json_path, scopes=SCOPES)
        self.service = build("drive", "v3", credentials=creds)

    def upload_to_folder(self, folder_id, filename, content_bytes, mime_type):
        file_metadata = {
            "name": filename,
            "parents": [folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(content_bytes), mimetype=mime_type, resumable=False)

        uploaded = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        return uploaded.get("id")