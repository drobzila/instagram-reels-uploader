import os
import io
import base64
from mega import Mega
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# -----------------------------
# 1) Google Drive setup
# -----------------------------
SERVICE_ACCOUNT_JSON_B64 = os.environ.get("SERVICE_ACCOUNT_JSON_B64")
FOLDER_ID = os.environ.get("FOLDER_ID")

service_json = base64.b64decode(SERVICE_ACCOUNT_JSON_B64).decode("utf-8")
with open("service.json", "w") as f:
    f.write(service_json)

SCOPES = ['https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file("service.json", scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(q=query).execute()
    return results.get('files', [])

def download_file(file_id, filename):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Downloading {filename}: {int(status.progress() * 100)}%")

# -----------------------------
# 2) Mega setup
# -----------------------------
MEGA_EMAIL = os.environ.get("MEGA_EMAIL")
MEGA_PASSWORD = os.environ.get("MEGA_PASSWORD")

mega = Mega()
m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

def upload_to_mega(local_file):
    file = m.upload(local_file)
    link = m.get_upload_link(file)
    print(f"Uploaded {local_file} → {link}")
    return link

# -----------------------------
# 3) Main
# -----------------------------
files = list_files_in_folder(FOLDER_ID)
print(f"Found {len(files)} files in Drive folder.")

for f in files:
    file_id = f['id']
    name = f['name']
    print(f"\nProcessing: {name}")

    download_file(file_id, name)
    upload_to_mega(name)
    os.remove(name)

print("\n🎉 All videos uploaded to Mega successfully!")
