import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from mega import Mega

# ---- إعداد Google Drive ----
SERVICE_ACCOUNT_JSON_B64 = os.environ['SERVICE_ACCOUNT_JSON_B64']
FOLDER_ID = os.environ['FOLDER_ID']

import base64, json
service_account_info = json.loads(base64.b64decode(SERVICE_ACCOUNT_JSON_B64))
creds = service_account.Credentials.from_service_account_info(service_account_info)
drive_service = build('drive', 'v3', credentials=creds)

# جلب الملفات داخل المجلد
results = drive_service.files().list(
    q=f"'{FOLDER_ID}' in parents and trashed=false",
    fields="files(id, name)"
).execute()
files = results.get('files', [])

if not files:
    print("No files found in Drive folder.")
else:
    print(f"Found {len(files)} file(s) in Drive folder.")

# ---- إعداد MEGA ----
MEGA_EMAIL = os.environ['MEGA_EMAIL']
MEGA_PASSWORD = os.environ['MEGA_PASSWORD']
mega = Mega()
m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

# رفع الملفات
for f in files:
    file_id = f['id']
    file_name = f['name']
    print(f"Downloading {file_name} from Drive...")
    
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%")

    fh.seek(0)
    
    print(f"Uploading {file_name} to MEGA...")
    m.upload(fh, file_name)
    print(f"{file_name} uploaded successfully!")
