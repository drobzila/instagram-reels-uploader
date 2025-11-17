import os
import gdown
from instagrapi import Client

# -----------------------------------
# الإعدادات
# -----------------------------------
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"  # من رابط المجلد
DOWNLOAD_FOLDER = "videos"
SESSION_FILE = "session.json"
CAPTION = "نسمات القرآن 🌿🤍\n#القرآن #تلاوة #quran"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# -----------------------------------
# تسجيل الدخول باستخدام session.json
# -----------------------------------
def instagram_login():
    cl = Client()
    if not os.path.exists(SESSION_FILE):
        print("❌ ملف session.json غير موجود!")
        return None
    print("🔐 تسجيل الدخول باستخدام session.json ...")
    cl.load_settings(SESSION_FILE)
    try:
        cl.login()
        print("✅ تسجيل الدخول ناجح")
    except Exception as e:
        print("❌ فشل تسجيل الدخول:", e)
        return None
    return cl

# -----------------------------------
# تحميل كل الفيديوهات من المجلد
# -----------------------------------
def download_all_from_drive(folder_id):
    print("⏳ جاري تحميل الفيديوهات من Google Drive folder:", folder_id)
    gdown.download_folder(id=folder_id, output=DOWNLOAD_FOLDER, quiet=False, use_cookies=False)
    files = [os.path.join(DOWNLOAD_FOLDER, f)
             for f in os.listdir(DOWNLOAD_FOLDER)
             if f.lower().endswith(".mp4")]
    if not files:
        print("⚠️ لا توجد فيديوهات mp4 في المجلد.")
    else:
        print("✅ تم تحميل الفيديوهات:")
        for f in files:
            print(" -", f)
    return files

# -----------------------------------
# رفع الفيديوهات إلى Instagram Reels
# -----------------------------------
def upload_reels(cl, files):
    for i, video in enumerate(files, start=1):
        print(f"\n🎬 رفع الفيديو رقم {i}: {video}")
        try:
            cl.clip_upload(video, CAPTION)
            print("🚀 تم رفع الريل بنجاح:", video)
        except Exception as e:
            print("❌ فشل رفع الفيديو:", video, "| الخطأ:", e)

# -----------------------------------
# MAIN
# -----------------------------------
if __name__ == "__main__":
    cl = instagram_login()
    if cl is None:
        exit(1)

    files = download_all_from_drive(FOLDER_ID)
    if files:
        upload_reels(cl, files)
    else:
        print("🔁 لا عمليات رفع لأن لا فيديوهات تم تحميلها.")
