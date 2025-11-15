import os
import json
import base64
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- قراءة الـ Base64 ---
b64 = os.environ.get("SERVICE_ACCOUNT_JSON_B64")

if not b64:
    raise Exception("❌ المتغير SERVICE_ACCOUNT_JSON_B64 غير موجود أو فارغ")

# --- فك Base64 ---
try:
    sa_json = base64.b64decode(b64).decode("utf-8")
except Exception as e:
    raise Exception("❌ فشل فك التشفير Base64:", e)

# --- تحويله JSON ---
try:
    info = json.loads(sa_json)
except Exception as e:
    raise Exception("❌ الخدمة ليست JSON صحيح:", e)

# --- إعداد الـ API ---
creds = Credentials.from_service_account_info(
    info,
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)

service = build("drive", "v3", credentials=creds)

# --- جلب الفيديوهات ---
query = "mimeType contains 'video/'"

results = service.files().list(
    q=query,
    fields="files(id, name)",
    pageSize=1000
).execute()

files = results.get("files", [])

print("عدد الملفات:", len(files))
print("\n--- روابط الفيديوهات ---")

for f in files:
    print(f"https://drive.google.com/uc?id={f['id']}  # {f['name']}")
