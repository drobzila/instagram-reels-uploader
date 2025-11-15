import os
import io
import json
import base64
import random
import datetime
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# 📋 إعدادات Instagram
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

# 📋 قائمة العناوين الجاهزة
video_titles = [
    "تلاوة خاشعة تلامس القلوب", 
    "صوت يريح القلب والعقل", 
    "آيات تبعث الطمأنينة في النفس",
    # … أكمل باقي العناوين كما تريد
]

# 🧭 مجلد الفيديوهات في Google Drive
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

# 🧩 خدمة Google Drive باستخدام SERVICE_ACCOUNT_JSON_B64
def get_drive_service():
    service_account_b64 = os.getenv("SERVICE_ACCOUNT_JSON_B64")
    if not service_account_b64:
        raise ValueError("❌ لم يتم تحديد SERVICE_ACCOUNT_JSON_B64 في البيئة")

    service_account_info = json.loads(base64.b64decode(service_account_b64))
    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build('drive', 'v3', credentials=credentials)

# 🧠 إنشاء عنوان فريد
def make_unique_title():
    return random.choice(video_titles)

# 🔗 إنشاء رابط تنزيل مباشر من Google Drive
def make_direct_drive_link(file_id):
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# 🎥 رفع الفيديو إلى Instagram Reels عبر video_url
def upload_video_to_instagram(video_url, caption):
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    payload = {
        "video_url": video_url,
        "caption": caption,
        "media_type": "REELS",
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, data=payload)
    res = r.json()
    container_id = res.get("id")
    if not container_id:
        print("❌ خطأ في إنشاء container:", res)
        return

    # نشر الفيديو
    publish_url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish"
    publish_res = requests.post(publish_url, data={
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN
    }).json()
    print("✅ نشر الفيديو:", publish_res)

# 🚀 الكود الرئيسي
def main():
    tz = datetime.timezone(datetime.timedelta(hours=1))  # الجزائر +1
    now = datetime.datetime.now(tz)

    drive_service = get_drive_service()

    files = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
        fields="files(id, name)"
    ).execute().get("files", [])

    if not files:
        print("⚠️ لا توجد فيديوهات في المجلد.")
        return

    random.shuffle(files)
    selected_files = files[:5]  # رفع 5 فيديوهات عشوائيًا

    for file in selected_files:
        original_title = file["name"]
        caption = make_unique_title()
        video_url = make_direct_drive_link(file["id"])

        print(f"⬇️ رفع {original_title} باستخدام الرابط المباشر: {video_url}")
        upload_video_to_instagram(video_url, caption)

    print("✅ تم رفع الفيديوهات على Instagram Reels بنجاح.")

if __name__ == "__main__":
    main()
