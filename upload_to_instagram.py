import os
import requests
import time

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]
OWNER = os.environ["GITHUB_OWNER"]
REPO = os.environ["GITHUB_REPO"]

# جلب روابط الفيديوهات من أحدث Release
r = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest").json()
videos = [a["browser_download_url"] for a in r.get("assets", []) if a["name"].endswith(".mp4")]

if not videos:
    print("❌ لم يتم العثور على أي فيديوهات في أحدث Release. تأكد من أن الفيديوهات موجودة في Assets.")
    exit(1)

def create_container(video_url):
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, data=payload).json()
    return r.get("id"), r.get("error")

def check_status(container_id):
    url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={ACCESS_TOKEN}"
    r = requests.get(url).json()
    return r.get("status_code")

def publish_media(container_id):
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    payload = {"creation_id": container_id, "access_token": ACCESS_TOKEN}
    r = requests.post(url, data=payload).json()
    return r

import tqdm
for video_url in tqdm.tqdm(videos, desc="رفع الفيديوهات"):
    print(f"\n🎬 رفع: {video_url}")
    container_id, error = create_container(video_url)
    if error:
        print("❌ خطأ في إنشاء container:", error)
        continue

    # الانتظار حتى يصبح الفيديو جاهزًا
    for attempt in range(10):
        status = check_status(container_id)
        print(f"⏳ حالة الفيديو: {status}, محاولة {attempt+1}/10")
        if status == "READY":
            print("✅ الفيديو جاهز للنشر!")
            break
        time.sleep(15)
    else:
        print("❌ الفيديو لم يصبح جاهزاً بعد الحد الأقصى من المحاولات.")
        continue

    result = publish_media(container_id)
    print("✅ نشر الفيديو:", result)
