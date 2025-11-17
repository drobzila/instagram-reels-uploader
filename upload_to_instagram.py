import os
import gdown
from instagrapi import Client

# ---------------------------------------
# 1. تسجيل الدخول إلى Instagram
# ---------------------------------------
USERNAME = os.getenv("IG_USERNAME")  # أو اكتب مباشرة: "your_username"
PASSWORD = os.getenv("IG_PASSWORD")  # أو اكتب مباشرة: "your_password"

if not USERNAME or not PASSWORD:
    print("❌ خطأ: تأكد من وضع IG_USERNAME و IG_PASSWORD")
    exit(1)

cl = Client()

print("🔐 تسجيل الدخول إلى Instagram...")
try:
    cl.login(USERNAME, PASSWORD)
    print("✅ تسجيل الدخول ناجح!")
except Exception as e:
    print("❌ خطأ أثناء تسجيل الدخول:", e)
    exit(1)

# ---------------------------------------
# 2. تحميل الفيديوهات من Google Drive
# ---------------------------------------
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"  # ضع Folder ID هنا

DOWNLOAD_FOLDER = "videos"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

print("⏳ جاري تحميل الفيديوهات من Google Drive...")

try:
    gdown.download_folder(
        id=FOLDER_ID,
        output=DOWNLOAD_FOLDER,
        quiet=False,
        use_cookies=False
    )
    print(f"✅ تم تحميل الفيديوهات إلى: {DOWNLOAD_FOLDER}")
except Exception as e:
    print("❌ فشل تحميل الفيديوهات من Drive:", e)
    exit(1)

# ---------------------------------------
# 3. جلب الفيديوهات mp4
# ---------------------------------------
videos = [
    os.path.join(DOWNLOAD_FOLDER, f)
    for f in os.listdir(DOWNLOAD_FOLDER)
    if f.lower().endswith(".mp4")
]

if not videos:
    print("⚠️ لا يوجد أي فيديو MP4 في مجلد Drive")
    exit(0)

print("🎥 الفيديوهات التي سيتم رفعها:")
for v in videos:
    print(" -", v)

# ---------------------------------------
# 4. رفع الفيديوهات إلى Reels
# ---------------------------------------
def upload_reel(video_path):
    print(f"🚀 رفع: {video_path}")
    try:
        cl.clip_upload(
            video_path,
            caption="تم النشر تلقائيًا من Google Drive 🤖"
        )
        print("✅ تم النشر بنجاح!")
    except Exception as e:
        print("❌ خطأ أثناء النشر:", e)

for video in videos:
    upload_reel(video)
