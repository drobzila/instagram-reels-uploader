import os
import json
import time
import random
import requests

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

video_titles = [
    "تلاوة خاشعة تلامس القلوب",
    "صوت يريح القلب والعقل",
    "آيات تبعث الطمأنينة",
    "من أجمل ما قرأ",
]

def upload_reel(video_url, caption):
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

    p = requests.post(publish_url, data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }).json()

    print("نتيجة النشر:", p)
    return True


def main():
    with open("videos.json", "r", encoding="utf8") as f:
        videos = json.load(f)

    print(f"رفع {len(videos)} فيديو...")

    for v in videos:
        title = random.choice(video_titles)
        print("🔹 رفع:", v["name"])

        success = upload_reel(v["url"], title)

        if success:
            print("✅ تم النشر")
        else:
            print("❌ فشل النشر")

        time.sleep(10)  # استراحة بسيطة

if __name__ == "__main__":
    main()
