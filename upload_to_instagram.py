import os
import requests
import time

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]
OWNER = os.environ["GITHUB_OWNER"]
REPO = os.environ["GITHUB_REPO"]

# جلب أحدث Release
release_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
r = requests.get(release_url).json()

# Debug: عرض JSON كامل للتأكد من وجود الفيديوهات
print("DEBUG: Release JSON =", r)

# استخراج روابط ملفات الفيديو mp4
videos = [a["browser_download_url"] for a in r.get("assets", []) if a["name"].endswith(".mp4")]

if not videos:
    print("❌ لم يتم العثور على أي فيديوهات في أحدث Release. تأكد من أن الفيديوهات موجودة في Assets.")
    exit(1)

print(f"✅ تم العثور على {len(videos)} فيديوهات: {videos}")

def upload(video_url):
    print("🎬 رفع:", video_url)
    container = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={"media_type":"REELS","video_url":video_url,"access_token":ACCESS_TOKEN}
    ).json()
    cid = container.get("id")
    if not cid:
        print("❌ خطأ إنشاء container", container)
        return
    for attempt in range(15):
        status = requests.get(
            f"https://graph.facebook.com/v19.0/{cid}",
            params={"fields":"status_code","access_token":ACCESS_TOKEN}
        ).json()
        if status.get("status_code")=="READY":
            print("✅ الفيديو جاهز للنشر")
            break
        print(f"⏳ حالة الفيديو لم تصبح جاهزة بعد، محاولة {attempt+1}/15")
        time.sleep(10)
    else:
        print("❌ الفيديو لم يصبح جاهزًا بعد الحد الأقصى من المحاولات.")
        return
    pub = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
        data={"creation_id":cid,"access_token":ACCESS_TOKEN}
    ).json()
    print("✅ تم نشر الفيديو:", pub)

# رفع كل الفيديوهات
for v in videos:
    upload(v)
