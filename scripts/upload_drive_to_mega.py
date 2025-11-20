import os
import base64
import io
from googleapiclient.discovery import build
from google.oauth2 import service_account
from mega import Mega

# ==== إعداد Google Drive ====
SERVICE_ACCOUNT_JSON_B64 = os.environ['SERVICE_ACCOUNT_JSON_B64']
FOLDER_ID = os.environ['FOLDER_ID']

# فك تشفير JSON Service Account
service_account_info = base64.b64decode(SERVICE_ACCOUNT_JSON_B64)
credentials = service_account.Credentials.from_service_account_info(
    eval(service_account_info.decode())
)
drive_service = build('drive', 'v3', credentials=credentials)

# ==== جلب الملفات من المجلد ====
results = drive_service.files().list(
    q=f"'{FOLDER_ID}' in parents and trashed=false",
    fields="files(id, name, mimeType)"
).execute()
files = results.get('files', [])

if not files:
    print("No files found in Drive folder.")
else:
    print(f"Found {len(files)} file(s) in Drive folder.")

# ==== إعداد MEGA ====
MEGA_EMAIL = os.environ['MEGA_EMAIL']
MEGA_PASSWORD = os.environ['MEGA_PASSWORD']

mega = Mega()
m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

# ==== رفع الملفات ====
for file in files:
    file_id = file['id']
    file_name = file['name']
    
    # تحميل الملف مؤقتًا في الذاكرة
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = build('googleapiclient.http', 'MediaIoBaseDownload')
    downloader = build('googleapiclient.http', 'MediaIoBaseDownload', request=request, fd=fh)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Downloading {file_name}: {int(status.progress() * 100)}%")

    fh.seek(0)

    # حفظ مؤقت على القرص قبل الرفع
    tmp_path = f"/tmp/{file_name}"
    with open(tmp_path, "wb") as f:
        f.write(fh.read())

    # رفع إلى MEGA
    m.upload(tmp_path)
    print(f"Uploaded {file_name} to MEGA.")

    # حذف الملف مؤقتًا
    os.remove(tmp_path)
