import os
import io
import random
import datetime
import requests
import base64
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
SERVICE_ACCOUNT_JSON_B64 = os.getenv("SERVICE_ACCOUNT_JSON_B64")

video_titles = [
    "تلاوة خاشعة تلامس القلوب",
    "صوت يريح القلب والعقل",
    "آيات تبعث الطمأنينة في النفس",
    # ... باقي العناوين
]

FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

def get_drive_service():
    if not SERVICE_ACCOUNT_JSON_B64:
        raise ValueError("❌ لم يتم العثور على SERVICE_ACCOUNT_JSON_B64 في .env أو secrets")

    try:
        service_account_json = base64.b64decode(SERVICE_ACCOUNT_JSON_B64)
    except Exception as e:
        raise ValueError(f"❌ خطأ في فك Base64: {e}")

    try:
        service_account_info = json.loads(service_account_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Base64 غير صالح، لم ينتج JSON صحيح: {e}")

    credentials = ServiceAccountCredentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build('drive', 'v3', credentials=credentials)

# باقي الكود كما هو (تحميل الفيديو، رفعه على Reels، إلخ)

def main():
    tz = datetime.timezone(datetime.timedelta(hours=1))  # الجزائر +1
    now = datetime.datetime.now(tz)

    try:
        drive_service = get_drive_service()
    except ValueError as e:
        print(e)
        return

    files = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
        fields="files(id, name)"
    ).execute().get("files", [])

    if not files:
        print("⚠️ لا توجد فيديوهات في المجلد.")
        return

    random.shuffle(files)
    selected_files = files[:5]

    for file in selected_files:
        original_title = file["name"]
        caption = random.choice(video_titles)

        path = download_video_from_drive(file["id"], original_title, drive_service)
        upload_video_to_instagram(path, caption)
        os.remove(path)
        print(f"🧹 حذف {original_title} بعد الرفع")

    print("✅ تم رفع الفيديوهات على Instagram Reels بنجاح.")
