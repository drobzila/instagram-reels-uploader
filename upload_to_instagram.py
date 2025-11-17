import os, requests, time

# متغيرات الوصول
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]

# معلومات الريبو والـ Release
OWNER = "drobliza"
REPO = "instagram-reels-uploader"
RELEASE_TAG = "v1.0"  # الإصدار الذي تريد استخدامه

# جلب الفيديوهات من Release محدد
url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{RELEASE_TAG}"
r = requests.get(url).json()

if "message" in r:
    print("❌ خطأ GitHub API:", r["message"])
    exit(1)

videos = [
    a["browser_download_url"]
    for a in r.get("assets", [])
    if a["name"].endswith(".mp4")
]

if not videos:
    print("❌ لم يتم العثور على أي فيديوهات في Release:", RELEASE_TAG)
    exit(1)

print("🎥 الفيديوهات الموجودة داخل Release:")
for v in videos:
    print(" -", v)

def upload(video_url):
    print("🎬 رفع:", video_url)

    # 1) إنشاء Container لرفع الريلز
    container = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": "Uploaded automatically 🤖",
            "access_token": ACCESS_TOKEN
        }
    ).json()

    print("📦 Response:", container)

    if "id" not in container:
        print("❌ فشل إنشاء Container:", container)
        return

    container_id = container["id"]

    # 2) نشر الريلز
    publish = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": ACCESS_TOKEN
        }
    ).json()

    print("🚀 Publish:", publish)


# رفع كل فيديو
for v in videos:
    upload(v)
    time.sleep(10)
