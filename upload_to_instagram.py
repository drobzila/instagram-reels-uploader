import os
import requests
import time
from datetime import datetime

# ---------- إعدادات Instagram ----------
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")  # Access Token
IG_USER_ID = os.environ.get("IG_USER_ID")     # IG User ID المرتبط بالصفحة

# ---------- إعدادات GitHub ----------
GITHUB_OWNER = "drobliza"  # صاحب المستودع
GITHUB_REPO = "instagram-reels-uploader"  # اسم المستودع
GITHUB_RELEASE_TAG = "latest"  # أو Tag معين
DAILY_LIMIT = 5  # عدد الفيديوهات التي تريد رفعها يوميًا

# ---------- جلب روابط الفيديوهات من Release ----------
def get_release_videos(owner, repo, tag="latest"):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/{tag}"
    r = requests.get(url)
    if r.status_code != 200:
        print("❌ فشل الحصول على Release")
        return []

    data = r.json()
    assets = data.get("assets", [])
    videos = [a["browser_download_url"] for a in assets if a["name"].endswith(".mp4")]
    return videos[:DAILY_LIMIT]

# ---------- رفع الفيديو إلى Instagram ----------
def create_container(video_url):
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, data=payload).json()
    if r.get("error"):
        print("❌ خطأ في إنشاء container:", r["error"])
        return None
    return r.get("id")

def check_status(container_id):
    url = f"https://graph.facebook.com/v19.0/{container_id}"
    params = {"fields": "status_code", "access_token": ACCESS_TOKEN}
    r = requests.get(url, params=params).json()
    return r.get("status_code")

def publish(container_id):
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    payload = {"creation_id": container_id, "access_token": ACCESS_TOKEN}
    r = requests.post(url, data=payload).json()
    return r

def upload_reel(video_url):
    print("\n🎬 رفع الفيديو:", video_url)
    container = create_container(video_url)
    if not container:
        return

    for attempt in range(15):
        status = check_status(container)
        if status == "READY":
            print("✅ الفيديو جاهز للنشر")
            break
        print(f"⏳ حالة الفيديو: {status}, محاولة {attempt+1}/15")
        time.sleep(10)
    else:
        print("❌ الفيديو لم يصبح جاهزاً بعد الحد الأقصى من المحاولات")
        return

    result = publish(container)
    print("📌 تم نشر الفيديو:", result)

# ---------- تنفيذ العملية ----------
if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n🚀 بدء رفع فيديوهات يوم {today}")

    videos_today = get_release_videos(GITHUB_OWNER, GITHUB_REPO, GITHUB_RELEASE_TAG)
    print(f"✅ عدد الفيديوهات الجاهزة اليوم: {len(videos_today)}")

    for video in videos_today:
        upload_reel(video)
        time.sleep(5)
