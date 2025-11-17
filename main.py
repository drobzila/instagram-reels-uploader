import os
import json
import base64
import requests
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from instagrapi import Client

# -----------------------------------
# إعدادات
# -----------------------------------
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"
DOWNLOAD_FOLDER = "videos"
CAPTION = "نسمات القرآن 🌿🤍\n#القرآن #تلاوة #quran"
SESSION_FILE = "session.json"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# -----------------------------------
# 1️⃣ جلب روابط الفيديوهات من Drive
# -----------------------------------
def get_drive_service():
    b64 = os.environ.get("SERVICE_ACCOUNT_JSON_B64")
    if not b64:
        raise Exception("❌ SERVICE_ACCOUNT_JSON_B64 غير موجود")
    info = json.loads(base64.b64decode(b64))
    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)

def fetch_videos_links():
    drive = get_drive_service()
    results = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
        fields="files(id, name)",
        pageSize=1000
    ).execute()
    files = results.get("files", [])
    if not files:
        print("⚠️ لا توجد فيديوهات.")
        return []

    links = []
    with open("videos.txt", "w", encoding="utf-8", newline="\n") as f:
        for file in files:
            link = f"https://drive.google.com/uc?id={file['id']}"
            f.write(link + "\n")
            links.append(link)
            print(f"🔗 {link}  # {file['name']}")
    print(f"\n✅ تم حفظ {len(links)} روابط في videos.txt")
    return links

# -----------------------------------
# 2️⃣ تحميل الفيديوهات من Drive
# -----------------------------------
def download_from_drive(url, output_path):
    print(f"⬇️ تحميل: {output_path}")
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise Exception(f"خطأ أثناء التحميل من {url}")
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(1024*1024):
            f.write(chunk)
    print("✔️ تم التحميل")
    return output_path

# -----------------------------------
# 3️⃣ تسجيل الدخول باستخدام session.json
# -----------------------------------
def login_with_session():
    cl = Client()
    if not os.path.exists(SESSION_FILE):
        raise Exception("❌ ملف session.json غير موجود في جذر المشروع!")
    cl.load_settings(SESSION_FILE)
    cl.login(cl.settings.get("authorization_data", {}).get("ds_user_id"),
             cl.settings.get("authorization_data", {}).get("sessionid"))
    print("✔️ تسجيل الدخول ناجح")
    return cl

# -----------------------------------
# 4️⃣ رفع الفيديوهات مع force_audio=True
# -----------------------------------
def upload_reel(cl, video_path):
    print(f"📤 رفع: {video_path}")
    try:
        cl.clip_upload(video_path, CAPTION, force_audio=True)
        print("✔️ تم رفع الريل")
    except Exception as e:
        print(f"❌ فشل رفع الريل: {e}")

# -----------------------------------
# MAIN
# -----------------------------------
def main():
    cl = login_with_session()
    links = fetch_videos_links()
    if not links:
        print("❌ لا يوجد روابط لرفعها.")
        return

    for i, url in enumerate(links, start=1):
        video_file = os.path.join(DOWNLOAD_FOLDER, f"video_{i}.mp4")
        download_from_drive(url, video_file)
        upload_reel(cl, video_file)
        os.remove(video_file)
        print(f"🗑️ تم حذف: {video_file}")

    print("\n🎉 انتهى كل شيء بنجاح!")

if __name__ == "__main__":
    main()
