import requests
import time
from tqdm import tqdm
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # تأكد من تعريفه في البيئة
IG_USER_ID = os.getenv("IG_USER_ID")      # ID حساب Instagram Business

MAX_ATTEMPTS = 15       # أقصى عدد محاولات للتحقق من جاهزية الفيديو
WAIT_SECONDS = 60       # الانتظار بين كل محاولة (بالثواني)

def create_container(video_url, caption):
    """إنشاء Media Container على Instagram"""
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "VIDEO",       # تحديد نوع الوسائط
        "video_url": video_url,      # رابط الفيديو المباشر
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, data=payload)
    data = r.json()
    if "id" in data:
        return data["id"]
    print(f"❌ خطأ في إنشاء container: {data}")
    return None

def check_media_status(media_id):
    """التحقق من حالة الوسائط"""
    url = f"https://graph.facebook.com/v17.0/{media_id}?fields=status_code&access_token={ACCESS_TOKEN}"
    r = requests.get(url)
    data = r.json()
    return data.get("status_code", "ERROR")

def publish_media(media_id):
    """نشر الفيديو بعد أن يصبح جاهز"""
    url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish"
    payload = {"creation_id": media_id, "access_token": ACCESS_TOKEN}
    r = requests.post(url, data=payload)
    data = r.json()
    if "id" in data:
        print(f"✅ الفيديو نشر بنجاح: {data['id']}")
    else:
        print(f"❌ فشل النشر: {data}")

def wait_until_ready(media_id):
    """انتظار حتى يصبح الفيديو جاهزًا"""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        status = check_media_status(media_id)
        if status == "READY":
            return True
        print(f"⏳ الفيديو ليس جاهزاً بعد (حالة: {status}), محاولة {attempt}/{MAX_ATTEMPTS}...")
        time.sleep(WAIT_SECONDS)
    print("❌ الفيديو لم يصبح جاهزاً بعد الحد الأقصى من المحاولات.")
    return False

def main():
    if not os.path.exists("videos.txt"):
        print("❌ ملف videos.txt غير موجود!")
        return

    # قراءة الفيديوهات من ملف النصوص
    videos = []
    with open("videos.txt", "r", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if line:
                # تقسيم الرابط والاسم
                if "# " in line:
                    url, title = line.split("# ", 1)
                    url, title = url.strip(), title.strip()
                else:
                    url, title = line, "بدون عنوان"
                videos.append({"url": url, "title": title})

    print(f"🔹 سيتم رفع {len(videos)} فيديو...")

    # رفع الفيديوهات مع شريط تقدم
    for video in tqdm(videos, desc="رفع الفيديوهات", unit="فيديو"):
        media_id = create_container(video["url"], video["title"])
        if not media_id:
            continue
        if wait_until_ready(media_id):
            publish_media(media_id)

if __name__ == "__main__":
    main()
