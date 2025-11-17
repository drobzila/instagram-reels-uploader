import os
import requests
import time

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]

# ضع هنا اسم حسابك واسم المستودع مباشرة
OWNER = "drobliza"
REPO = "instagram-reels-uploader"

# جلب الفيديوهات من أحدث Release
url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
r = requests.get(url, headers={"Authorization": f"token {os.environ.get('MY_GITHUB_TOKEN', '')}"}).json()

videos = [
    a["browser_download_url"]
    for a in r.get("assets", [])
    if a["name"].endswith(".mp4")
]

if not videos:
    print("❌ لم يتم العثور على أي فيديوهات في أحدث Release.")
    exit(1)

print("🎥 الفيديوهات الموجودة داخل Release:")
for v in videos:
    print(" -", v)


def upload(video_url):
    print("\n🎬 رفع:", video_url)

    # 1) إنشاء Container للريلز
    container = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": "Uploaded automatically 🤖",
            "access_token": ACCESS_TOKEN
        }
    ).json()

    print("📦 Container Response:", container)

    if "id" not in container:
        print("❌ فشل إنشاء Container:", container)
        return

    container_id = container["id"]

    # 2) الانتظار حتى يصبح الفيديو جاهز للنشر
    print("⏳ التحقق من جاهزية الفيديو للنشر…")
    for _ in range(30):  # 30 محاولة × 5 ثواني = حتى 2.5 دقيقة
        status = requests.get(
            f"https://graph.facebook.com/v19.0/{container_id}",
            params={"fields": "status_code", "access_token": ACCESS_TOKEN}
        ).json()

        if status.get("status_code") == "FINISHED":
            print("✅ الفيديو جاهز للنشر")
            break
        else:
            print("⏳ الفيديو لم يجهز بعد، ننتظر 5 ثواني…")
            time.sleep(5)
    else:
        print("❌ الفيديو لم يجهز بعد بعد 2.5 دقيقة")
        return

    # 3) نشر الريلز
    publish = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": ACCESS_TOKEN
        }
    ).json()

    print("🚀 Publish Response:", publish)


# رفع كل فيديو
for v in videos:
    upload(v)
    time.sleep(10)  # انتظار قصير قبل الفيديو التالي
