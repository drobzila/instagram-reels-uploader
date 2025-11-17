import os
import gdown
from instagrapi import Client

# -------------------------------------------
# الإعدادات من GitHub Secrets
# -------------------------------------------

FOLDER_ID = os.getenv("FOLDER_ID")
DOWNLOAD_FOLDER = "videos"
SESSION_FILE = "session.json"
CAPTION = "نسمات القرآن 🌿🤍\n#القرآن #تلاوة #quran"

if not FOLDER_ID:
    print("❌ خطأ: لم يتم تحديد FOLDER_ID من GitHub Secrets")
    exit(1)

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# -------------------------------------------
# تسجيل الدخول عبر session.json
# -------------------------------------------

def instagram_login():
    cl = Client()
    if not os.path.exists(SESSION_FILE):
        print("❌ ملف session.json غير موجود!")
        return None

    print("🔐 تسجيل الدخول باستخدام session.json ...")
    cl.load_settings(SESSION_FILE)

    try:
        cl.login()  # استخدام الجلسة لتسجيل الدخول
        print("✅ تسجيل الدخول ناجح")
    except Exception as e:
        print("❌ فشل تسجيل الدخول:", e)
        return None

    return cl

# -------------------------------------------
# تحميل الفيديوهات من Google Drive
# -------------------------------------------

def download_from_drive():
    print("⏳ جاري تحميل الفيديوهات من Google Drive...")

    gdown.download_folder(
        id=FOLDER_ID,
        output=DOWNLOAD_FOLDER,
        quiet=False,
        use_cookies=False
    )

    files = [
        os.path.join(DOWNLOAD_FOLDER, f)
        for f in os.listdir(DOWNLOAD_FOLDER)
        if f.lower().endswith(".mp4")
    ]

    if not files:
        print("❌ لا توجد فيديوهات في المجلد!")
        return []

    print("✅ تم تحميل الفيديوهات:")
    for f in files:
        print(" -", f)

    return files

# -------------------------------------------
# رفع الفيديوهات إلى Instagram Reels
# -------------------------------------------

def upload_reels(cl, files):
    for video in files:
        print(f"\n🎬 رفع الفيديو: {video}")
        try:
            cl.clip_upload(video, CAPTION)
            print("🚀 تم رفع الريل بنجاح")
        except Exception as e:
            print("❌ فشل رفع الفيديو:", e)

# -------------------------------------------
# MAIN
# -------------------------------------------

if __name__ == "__main__":
    cl = instagram_login()
    if cl is None:
        exit()

    files = download_from_drive()
    if files:
        upload_reels(cl, files)
