import os
import io
import random
import datetime
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials

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

# 🧩 خدمة Google Drive باستخدام JSON مباشر
SERVICE_ACCOUNT_JSON = {
  "type": "service_account",
  "project_id": "quran-478116",
  "private_key_id": "9afa7d003241409eab8c46514cdb1bdcebe192fe",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC61sax194Qban3\nCBDZfkdpahT7fRKMIDC2Jd42wzCV9BeLwUyxKDqkTbpT59fmvT9L7b++IHsx+Af0\nUCi9BSZQ2cRhpY0LueaMBxZ2Ov++HosL5bOIHhvAUByAqwUslSAVTtvdKgWNCP7Q\nlifyuPcuYhtk6jlBtTsz9OknN5/DobxC6PW/7Z1kQcTfgxGt9eRiXIGcjMdIzMAu\n/yJX/38bt6khxaCZiYF94rrMzOJI7NnXjexEeh0JmW6rDbnQhCgsQ4r2mOPYxq3f\nhAVcfarV8M4qC0yrpwOQg+n7jonw8e0lZRc+y1cjtyKcHc7rqCw0LmKpdhwaV4Cj\nJn3mPgctAgMBAAECggEAPJmZ86fxAkIXfSTUFj8TmXjLWnCMOf/c3M92fiucEB8O\nHgmxvsouDwmY9Er/53qdU5rG9LtjSedJaTAwrnJDpbikLgm8sD95LBTGb82eEoOk\nlNTJgM5HMP6q5/7QXE/4CoE75cWR7FctEumJBnyAy74NZZNkw8+s5qK6lro/avt2\nDdc/piaHDZElmgslokRHFG0609GRfEYeKZUM9nNOL42Ni+DOBW4y/TZyw7EbV8OY\n8TFRH6OjCCw5Mdi2E3c6tsqR8hERb2HqYg7Yn8swFt4X5hYigQEIC7kkbLIqToNL\nsri78pxYHedVO2qpVa6NQO13QXuO2Myyt1kEbUMm/wKBgQDa1oDMF/KoNQYlgARV\nDWe1ORRiitdtv1QeON/50TwSKfnNJR3+8Ya4k3u1DhfEPIyei7BZVbrBIphHDULh\n+nthhIUTr6kmt9qLyfwvdIizzK1kZrYsWz9QfoJwCzXNyBp6StJCovxeFbAxDOaO\n38o+TJrnqx7HerUxnlW6o9c89wKBgQDakTCSFFgu3XfQNOUH9y2uuOOj8vysSGx4\nOQIPm9FoAhsP0owEaL0Evf5E+hzswaEhgguo/yEeeK2X6HA2LPvYY40OHNnKKojp\nHP0cnG3bmD1143a+hSw17K/mFAk8lPjIPC+Y2ey5KWVzzKyoc8dM838TpmJ0ZU0n\n4iC0DqmH+wKBgCEsqWPHMZr8Rs1CheWa3aDkYUm7AIN7oLXgK1wEsxWR1XOa79wp\nIyIyAWvmEgZGo46ZYId6bpA+vVTwFraJMVEMNNxSIdNjxbaxTRComtye554zz+QT\nhRqfwwhXOrXSYuktFIjTimx83zPgX8dC97bQCB+cmlLlMDiwZxCfK87rAoGBAJdz\nK9jNSB2RUMhxHpLacEk1zGd6pCMtPBxCRG9UZVJQwze/iU401WVH0b0yIoDb2y9A\n0ZuUzfozXPZ6Fec0XH6g3Mj+rNsthhkiATGmI2maoFvj9hAmb3AeRfSDxbK493qo\nWcLsnt/fE3GeTbWcJGnqABA5ptdIqqIMSuT5k/epAoGBAMf77nLW5iZHxYB8bjVp\n2cWbtnvH/yMRRRNdeWSkV/RZDOGKWcGBSRER/HbbW5Ti9Jr3qi6CDjGiiXXiX0EX\nnhVWrJ+EXx4SDKGDpCUt/g5a7874FTpJCj/l192MTmBbr0I8G24rrhnLzGuJMIEC\neUYV6/SM0xYTOKBZSKJ4aETw\n-----END PRIVATE KEY-----\n",
  "client_email": "quran-833@quran-478116.iam.gserviceaccount.com",
  "client_id": "115882713836588740161",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/quran-833%40quran-478116.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

def get_drive_service():
    credentials = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_JSON,
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

# 🎥 رفع الفيديو إلى Instagram Reels
def upload_video_to_instagram(video_path, caption):
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    files = {'file': open(video_path, 'rb')}
    payload = {
        "caption": caption,
        "media_type": "REELS",  # لا تستخدم VIDEO، يجب REELS
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, files=files, data=payload)
    res = r.json()
    container_id = res.get("id")
    if not container_id:
        print("❌ خطأ في إنشاء container:", res)
        files['file'].close()
        return

    # نشر الفيديو
    publish_url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish"
    publish_res = requests.post(publish_url, data={
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN
    }).json()
    print("✅ نشر الفيديو:", publish_res)
    files['file'].close()

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

        path = download_video_from_drive(file["id"], original_title, drive_service)
        upload_video_to_instagram(path, caption)

        os.remove(path)
        print(f"🧹 حذف {original_title} بعد الرفع")

    print("✅ تم رفع الفيديوهات على Instagram Reels بنجاح.")

if __name__ == "__main__":
    main()
