import os
import json
import random
import datetime
import base64
import requests
from googleapiclient.discovery import build
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

# 🔗 الحصول على رابط عام للفيديو
def get_public_video_url(file_id, drive_service):
    # جعل الملف عام إذا لم يكن كذلك
    try:
        drive_service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
            fields="id"
        ).execute()
    except Exception as e:
        print("⚠️ فشل في جعل الملف عام:", e)

    # رابط مباشر للتحميل من Google Drive
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# 🧠 إنشاء عنوان فريد
def make_unique_title(used_titles):
    title = random.choice(video_titles)
    while title in used_titles:
        title = random.choice(video_titles)
    used_titles.add(title)
    return title

# 🎥 رفع الفيديو إلى Instagram Reels
def upload_video_to_instagram(video_url, caption):
    # إنشاء container
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    payload = {
        "video_url": video_url,
        "caption": caption,
        "media_type": "VIDEO",
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
    used_titles = set()

    files = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
        fields="files(id, name)"
    ).execute().get("files", [])

    if not files:
        print("⚠️ لا توجد فيديوهات في المجلد.")
        return

    random.shuffle(files)
    selected_files = files[:5]  # رفع 5 فيديوهات عشوائياً

    for file in selected_files:
        original_title = file["name"]
        caption = make_unique_title(used_titles)

        video_url = get_public_video_url(file["id"], drive_service)
        print(f"🌐 رفع الفيديو {original_title} عبر الرابط: {video_url}")

        upload_video_to_instagram(video_url, caption)

    print("✅ تم رفع الفيديوهات على Instagram Reels بنجاح.")

if __name__ == "__main__":
    main()
