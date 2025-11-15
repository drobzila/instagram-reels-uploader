import os
import io
import random
import datetime
import requests
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

# 📋 إعدادات Instagram
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

# 📋 قائمة العناوين الجاهزة
video_titles = [
    "تلاوة خاشعة تلامس القلوب", "صوت يريح القلب والعقل", "آيات تبعث الطمأنينة في النفس",
    # … أكمل باقي العناوين كما في الكود الأصلي
]

# 🧭 مجلد الفيديوهات في Google Drive
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

# 🧩 خدمة Google Drive
def get_drive_service():
    credentials = ServiceAccountCredentials.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build('drive', 'v3', credentials=credentials)

# 🧠 إنشاء عنوان فريد
def make_unique_title():
    return random.choice(video_titles)

# 🎥 رفع الفيديو إلى Instagram Reels باستخدام video_url
def upload_video_to_instagram(video_url, caption):
    # إنشاء Media Container
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    res = requests.post(url, data=payload).json()
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
    selected_files = files[:5]  # يمكن تعديل العدد

    for file in selected_files:
        original_title = file["name"]
        caption = make_unique_title()
        file_id = file["id"]

        # رابط مباشر للملف على Google Drive
        video_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        print(f"⬇️ رفع الفيديو: {original_title}")
        upload_video_to_instagram(video_url, caption)

    print("✅ تم رفع الفيديوهات على Instagram Reels بنجاح.")

if __name__ == "__main__":
    main()
