import os
import requests
import time

# ⚡ المتغيرات الأساسية
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]
GITHUB_TOKEN = os.environ["MY_GITHUB_TOKEN"]

OWNER = "drobliza"
REPO = "instagram-reels-uploader"

# جلب أحدث Release من GitHub
print("📦 جلب أحدث Release من GitHub...")
release_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
r = requests.get(release_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
if r.status_code != 200:
    print(f"❌ خطأ GitHub API: {r.status_code} - {r.text}")
    exit(1)

release_data = r.json()
videos = [
    asset["browser_download_url"]
    for asset in release_data.get("assets", [])
    if asset["name"].endswith(".mp4")
]

if not videos:
    print("❌ لم يتم العثور على أي فيديوهات في أحدث Release.")
    exit(1)

print("🎥 الفيديوهات الموجودة داخل Release:")
for v in videos:
    print(" -", v)

def upload_reel(video_url):
    print(f"\n🎬 رفع الفيديو: {video_url}")

    # 1️⃣ إنشاء Container
    container_res = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": "Uploaded automatically 🤖",
            "access_token": ACCESS_TOKEN
        }
    ).json()

    if "id" not in container_res:
        print(f"❌ فشل إنشاء Container: {container_res}")
        return

    container_id = container_res["id"]
    print(f"📦 Container ID: {container_id}")

    # 2️⃣ مراقبة جاهزية الوسائط تلقائيًا
    while True:
        status_res = requests.get(
            f"https://graph.facebook.com/v19.0/{container_id}",
            params={"access_token": ACCESS_TOKEN}
        ).json()

        state = status_res.get("status")
        if state == "FINISHED":
            print("✅ الوسائط جاهزة للنشر")
            break
        elif state is None:
            print(f"❌ لم يتم التعرف على حالة الفيديو: {status_res}")
            return
        else:
            print(f"⏳ الفيديو ليس جاهزًا بعد (حالة: {state})، إعادة المحاولة بعد 5 ثوانٍ...")
            time.sleep(5)

    # 3️⃣ نشر الفيديو
    publish_res = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": ACCESS_TOKEN
        }
    ).json()

    if "id" in publish_res:
        print(f"🚀 تم النشر بنجاح! Media ID: {publish_res['id']}")
    else:
        print(f"❌ خطأ عند النشر: {publish_res}")

# رفع كل الفيديوهات واحدة واحدة
for video in videos:
    upload_reel(video)
