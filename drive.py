import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# تحميل ملف الخدمة من المتغير البيئي
service_account_json = os.environ["SERVICE_ACCOUNT_JSON_B64"]
service_account_info = json.loads(service_account_json)

# إنشاء credentials
creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)

# إنشاء خدمة Google Drive API
service = build("drive", "v3", credentials=creds)

# جلب ملفات الفيديو فقط
results = service.files().list(
    q="mimeType contains 'video/'",
    fields="files(id, name, mimeType, webViewLink)"
).execute()

files = results.get("files", [])

print("\n=== قائمة عناوين الفيديوهات في Google Drive ===\n")

if not files:
    print("لا توجد فيديوهات.")
else:
    for f in files:
        print(f"- {f['name']}")
        print(f"  الرابط: {f['webViewLink']}\n")
