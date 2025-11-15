import time
import requests
from tqdm import tqdm

ACCESS_TOKEN = "EAAP185xzqtYBP3cvZCV2stwf4k3lsaWR4Rf2dfngNkCyZBOggrA9TGujetwW8h52PRLpww2Q8snBIlHSdI93E9hUClIRVxNpoiBCMGeqWWMj5ZAZBMIe8yP9OzOlU9ZCKZB7FZBZAIKkQuQ7PqDJZAZBIN0yngE92mADe6okZAT4iw5iZCHsliHF2lfgTvzh44ZAZBENP9"
IG_USER_ID = "17841478336280146"

# جرب رابط فيديو مباشر صغير أولًا
videos = [
    "https://drive.google.com/uc?export=download&id=1VgMxWyIrZ9--tiTmZlfQjT0rYbxMsUSB"
]

def create_container(video_url):
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",  # مهم جدًا
        "video_url": video_url,
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, data=payload).json()
    print("Debug - create_container response:", r)  # <-- طباعة debug
    return r.get("id"), r.get("error")

def check_status(container_id):
    url = f"https://graph.facebook.com/v17.0/{container_id}?fields=status_code&access_token={ACCESS_TOKEN}"
    r = requests.get(url).json()
    print("Debug - check_status response:", r)  # <-- طباعة debug
    return r.get("status_code")

def publish_media(container_id):
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish"
    payload = {"creation_id": container_id, "access_token": ACCESS_TOKEN}
    r = requests.post(url, data=payload).json()
    print("Debug - publish_media response:", r)  # <-- طباعة debug
    return r

for video in tqdm(videos, desc="رفع الفيديوهات"):
    print(f"رفع الفيديو: {video}")
    container_id, error = create_container(video)
    if error:
        print("❌ خطأ في إنشاء container:", error)
        continue

    # الانتظار حتى يصبح الفيديو جاهزًا
    max_attempts = 10
    attempt_delay = 15  # ثانية
    for attempt in range(max_attempts):
        status = check_status(container_id)
        print(f"⏳ حالة الفيديو: {status}, محاولة {attempt+1}/{max_attempts}")
        if status == "READY":
            print("✅ الفيديو جاهز للنشر!")
            break
        time.sleep(attempt_delay)
    else:
        print("❌ الفيديو لم يصبح جاهزاً بعد الحد الأقصى من المحاولات.")
        continue

    # نشر الفيديو
    result = publish_media(container_id)
    print("✅ نشر الفيديو:", result)
