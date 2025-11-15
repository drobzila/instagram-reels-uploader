import time
import requests
from tqdm import tqdm

ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
IG_USER_ID = "YOUR_IG_USER_ID"

videos = [
    "https://drive.google.com/uc?id=1VgMxWyIrZ9--tiTmZlfQjT0rYbxMsUSB",
    "https://drive.google.com/uc?id=1NTclI5dtazAPB2e830sVR2eN8YhGeHJz",
    "https://drive.google.com/uc?id=1aJk-gxzIJOfC49XtGkfbRV6fPpZ-QPJt",
    "https://drive.google.com/uc?id=19mzAiTLOtYzrZ-CxftAFCp4PrjOfl-7X",
    "https://drive.google.com/uc?id=1F3Af__lPU3eqszwf_Xs_NePxBQke1Y6L"
]

def create_container(video_url):
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",  # مهم جدًا
        "video_url": video_url,
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, data=payload).json()
    return r.get("id"), r.get("error")

def check_status(container_id):
    url = f"https://graph.facebook.com/v17.0/{container_id}?fields=status_code&access_token={ACCESS_TOKEN}"
    r = requests.get(url).json()
    return r.get("status_code")

def publish_media(container_id):
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish"
    payload = {"creation_id": container_id, "access_token": ACCESS_TOKEN}
    r = requests.post(url, data=payload).json()
    return r

for video in tqdm(videos, desc="رفع الفيديوهات"):
    print(f"رفع: {video}")
    container_id, error = create_container(video)
    if error:
        print("❌ خطأ في إنشاء container:", error)
        continue

    # الانتظار حتى يصبح الفيديو جاهزًا
    max_attempts = 20
    attempt_delay = 30  # ثانية
    for attempt in range(max_attempts):
        status = check_status(container_id)
        print(f"⏳ حالة الفيديو: {status}, محاولة {attempt+1}/{max_attempts}")
        if status == "READY":
            break
        time.sleep(attempt_delay)
    else:
        print("❌ الفيديو لم يصبح جاهزاً بعد الحد الأقصى من المحاولات.")
        continue

    # نشر الفيديو
    result = publish_media(container_id)
    print("✅ نشر الفيديو:", result)
