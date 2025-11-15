import os
import time
import random
import requests
from tqdm import tqdm  # شريط التقدم

# 📋 إعدادات Instagram
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

# 📋 قائمة العناوين الجاهزة
video_titles = [
    "تلاوة خاشعة تلامس القلوب",
    "صوت يريح القلب والعقل",
    "آيات تبعث الطمأنينة",
    "من أجمل ما قرأ",
    "هدوء النفس والروح"
]

# 🧠 اختيار عنوان عشوائي
def make_unique_title():
    return random.choice(video_titles)

# 🎥 رفع فيديو إلى Instagram Reels مع التأكد من جاهزيته
def upload_video(video_url, caption):
    # 1️⃣ إنشاء الـ container
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
        print(f"❌ خطأ في إنشاء container: {res}")
        return False

    # 2️⃣ الانتظار حتى يصبح الفيديو جاهز للنشر
    max_attempts = 10
    for attempt in range(max_attempts):
        status_res = requests.get(
            f"https://graph.facebook.com/v17.0/{container_id}?fields=status_code&access_token={ACCESS_TOKEN}"
        ).json()
        status = status_res.get("status_code")
        if status == "READY":
            break
        print(f"⏳ الفيديو ليس جاهزاً بعد (حالة: {status}), محاولة {attempt+1}/{max_attempts}...")
        time.sleep(5)
    else:
        print("❌ الفيديو لم يصبح جاهزاً بعد الحد الأقصى من المحاولات.")
        return False

    # 3️⃣ نشر الفيديو
    publish_url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish"
    publish_res = requests.post(publish_url, data={
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN
    }).json()
    if publish_res.get("id"):
        print(f"✅ تم نشر الفيديو بنجاح: {caption}")
        return True
    else:
        print(f"❌ خطأ أثناء النشر: {publish_res}")
        return False

# 🚀 الكود الرئيسي
def main():
    if not os.path.exists("videos.txt"):
        print("❌ ملف videos.txt غير موجود!")
        return

    with open("videos.txt", "r", encoding="utf8") as f:
        videos = [line.strip().split("#")[0].strip() for line in f if line.strip()]

    print(f"\n🔹 سيتم رفع {len(videos)} فيديو...")

    for video_url in tqdm(videos, desc="رفع الفيديوهات", unit="فيديو"):
        caption = make_unique_title()
        upload_video(video_url, caption)
        time.sleep(3)  # فاصل بين الفيديوهات

if __name__ == "__main__":
    main()
