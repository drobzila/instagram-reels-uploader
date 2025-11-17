import os
import sys
import subprocess
from instagrapi import Client
from download_drive_videos import download_drive_videos  # السكربت الذي يجلب روابط الفيديوهات

# =====================
# إعداد المجلدات
# =====================
os.makedirs("videos", exist_ok=True)
os.makedirs("reencoded", exist_ok=True)

# =====================
# التأكد من تثبيت gdown
# =====================
try:
    import gdown
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "gdown"])
    import gdown

# =====================
# إعدادات Instagram
# =====================
SESSION_FILE = "session.json"  # موجود في جذر المشروع
CAPTION = "تم الرفع تلقائيًا بواسطة GitHub Actions"

cl = Client()
try:
    cl.load_settings(SESSION_FILE)
    print("✔️ تسجيل الدخول ناجح")
except Exception as e:
    print(f"❌ فشل تسجيل الدخول: {e}")
    sys.exit(1)

# =====================
# تحميل الفيديوهات من Google Drive
# =====================
video_links = download_drive_videos()  # دالة ترجع قائمة روابط الفيديو
print(f"✅ تم الحصول على {len(video_links)} روابط")

for idx, link in enumerate(video_links, 1):
    output_file = f"videos/video_{idx}.mp4"
    try:
        print(f"⬇️ تحميل: {link}")
        gdown.download(link, output_file, quiet=False)
        print(f"✔️ تم التحميل: {output_file}")
    except Exception as e:
        print(f"❌ فشل تحميل الفيديو: {link} | {e}")
        continue

    # رفع الفيديو إلى Instagram
    try:
        print(f"📤 رفع: {output_file}")
        cl.clip_upload(output_file, CAPTION)
        print(f"✅ تم رفع الفيديو: {output_file}")
    except Exception as e:
        print(f"❌ فشل رفع الريل: {e}")
    finally:
        # حذف الفيديو بعد الرفع أو الفشل لتوفير مساحة
        if os.path.exists(output_file):
            os.remove(output_file)
