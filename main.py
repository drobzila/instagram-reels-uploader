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

# ⬇️ تحميل الفيديو من Google Drive
def download_video_from_drive(file_id, file_name, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    print(f"⬇️ تم تحميل {file_name}")
    return file_name

# 🧠 إنشاء عنوان فريد
def make_unique_title():
    return random.choice(video_titles)

# 🎥 رفع الفيديو إلى Instagram Reels من الملف المحلي
def upload_video_to_instagram(video_path, caption):
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    with open(video_path, 'rb') as f:
        files = {'video_file': f}  # المفتاح video_file وليس file
        payload = {
            "caption": caption,
            "media_type": "REELS",  # يجب REELS
            "access_token": ACCESS_TOKEN
        }
        r = requests.post(url, files=files, data=payload)
        res = r.json()
    
    container_id = res.get("id")
    if not container_id:
        print("❌ خطأ في إنشاء container:", res)
        return
    
    # نشر الفيديو بعد التأكد من أن container جاهز
    publish_url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish"
    while True:
        publish_res = requests.post(publish_url, data={
            "creation_id": container_id,
            "access_token": ACCESS_TOKEN
        }).json()
        if "id" in publish_res:
            print("✅ نشر الفيديو:", publish_res)
            break
        elif publish_res.get("error", {}).get("code") == 9007:
            # الوسائط غير جاهزة بعد، انتظر 5 ثواني ثم حاول مجددًا
            print("⏳ الوسائط غير جاهزة، إعادة المحاولة بعد 5 ثواني...")
            import time; time.sleep(5)
        else:
            print("❌ خطأ أثناء النشر:", publish_res)
            break

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
    selected_files = files[:5]

    for file in selected_files:
        original_title = file["name"]
        caption = make_unique_title()

        # تحميل الفيديو مؤقتًا
        path = download_video_from_drive(file["id"], original_title, drive_service)

        # رفع الفيديو
        upload_video_to_instagram(path, caption)

        # حذف الملف بعد الرفع
        os.remove(path)
        print(f"🧹 حذف {original_title} بعد الرفع")

    print("✅ تم رفع الفيديوهات على Instagram Reels بنجاح.")

if __name__ == "__main__":
    main()
