import os
import time
from instagrapi import Client
from download_drive_videos import download_drive_videos  # السكربت الذي يجلب روابط الفيديوهات

SESSION_FILE = "session.json"
VIDEOS_FOLDER = "videos"
CAPTION = "Uploaded automatically 🤖"
DELAY_BETWEEN_UPLOADS = 600  # 10 دقائق، يمكن تعديلها بالثواني

def main():
    # 1️⃣ تسجيل الدخول باستخدام session
    cl = Client()
    cl.load_settings(SESSION_FILE)
    print("✔️ تسجيل الدخول ناجح")

    # 2️⃣ تحميل روابط الفيديوهات من Google Drive
    video_links = download_drive_videos()  # دالة من السكربت السابق، تُرجع قائمة روابط الفيديوهات
    print(f"✅ تم الحصول على {len(video_links)} روابط")

    # 3️⃣ رفع الفيديوهات واحدة واحدة مع فاصل زمني
    for idx, link in enumerate(video_links, start=1):
        video_path = os.path.join(VIDEOS_FOLDER, f"video_{idx}.mp4")

        # تحميل الفيديو
        print(f"⬇️ تحميل: {link}")
        # يمكنك استخدام gdown أو requests هنا حسب سكربتك
        os.system(f"gdown {link} -O {video_path}")

        if not os.path.exists(video_path):
            print(f"❌ فشل تحميل الفيديو: {link}")
            continue

        # رفع الريل
        try:
            print(f"📤 رفع: {video_path}")
            cl.clip_upload(video_path, CAPTION)
            print(f"🚀 تم رفع الفيديو بنجاح: {video_path}")
        except Exception as e:
            print(f"❌ فشل رفع الريل: {e}")

        # حذف الفيديو المؤقت
        if os.path.exists(video_path):
            os.remove(video_path)

        # انتظار قبل رفع الفيديو التالي
        if idx < len(video_links):
            print(f"⏳ الانتظار {DELAY_BETWEEN_UPLOADS} ثانية قبل رفع الفيديو التالي...")
            time.sleep(DELAY_BETWEEN_UPLOADS)

    print("🎉 انتهى كل شيء بنجاح!")

if __name__ == "__main__":
    main()
