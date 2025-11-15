import os
import random
import time
import requests

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

# قائمة العناوين الجاهزة
video_titles = [
    "تلاوة خاشعة تلامس القلوب",
    "صوت يريح القلب والعقل",
    "آيات تبعث الطمأنينة",
    "من أجمل ما قرأ",
]

def upload_reel(video_url, caption):
    """رفع فيديو على Instagram Reels"""
    create_url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }

    r = requests.post(create_url, data=payload)
    res = r.json()

    if "id" not in res:
        print("❌ خطأ في إنشاء container:", res)
        return False

    creation_id = res["id"]
    publish_url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish"
    publish_res = requests.post(publish_url, data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }).json()

    print("✅ نشر الفيديو:", publish_res)
    return True

def main():
    # التحقق من وجود videos.txt
    if not os.path.exists("videos.txt"):
        print("❌ لم يتم العثور على videos.txt")
        return

    # قراءة الروابط من videos.txt
    with open("videos.txt", "r", encoding="utf8") as f:
        lines = f.readlines()

    # تنظيف الخطوط (إزالة الفراغات)
    videos = [line.strip() for line in lines if line.strip()]

    print(f"🔹 سيتم رفع {len(videos)} فيديو...")

    for line in videos:
        # السطر بالشكل: URL  # اسم الفيديو
        parts = line.split("  # ")
        video_url = parts[0]
        video_name = parts[1] if len(parts) > 1 else "video"

        caption = random.choice(video_titles)
        print(f"رفع: {video_name} بعنوان: {caption}")

        upload_reel(video_url, caption)
        time.sleep(10)  # استراحة قصيرة بين الفيديوهات

if __name__ == "__main__":
    main()
