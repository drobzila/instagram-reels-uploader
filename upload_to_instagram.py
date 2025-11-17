import os, requests, time

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]

# اسم الحساب واسم المستودع مباشرة (لا تضع / داخل REPO)
OWNER = "drobliza"
REPO = "instagram-reels-uploader"

# جلب الفيديوهات من أحدث Release
url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
response = requests.get(url)

if response.status_code != 200:
    print("❌ API Error:", response.text)
    exit(1)

data = response.json()

# استخراج الروابط
videos = [
    a["browser_download_url"]
    for a in data.get("assets", [])
    if a["name"].endswith(".mp4")
]

if not videos:
    print("❌ لم يتم العثور على أي فيديوهات داخل Release!")
    print("🔍 محتوى release:", data.get("assets", []))
    exit(1)

print("🎥 الفيديوهات الموجودة داخل Release:")
for v in videos:
    print(" -", v)

def upload(video_url):
    print("\n🎬 رفع:", video_url)

    # 1) إنشاء Container
    container = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": "Uploaded automatically 🤖",
            "access_token": ACCESS_TOKEN
        }
    ).json()

    print("📦 Container response:", container)

    if "id" not in container:
        print("❌ فشل إنشاء Container. سيتم تجاوز هذا الفيديو.")
        return

    container_id = container["id"]

    # الانتظار ضروري حتى يكتمل المعالجة
    print("⏳ الانتظار 25 ثانية قبل النشر...")
    time.sleep(25)

    # 2) نشر الفيديو
    publish = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": ACCESS_TOKEN
        }
    ).json()

    print("🚀 Publish response:", publish)


# رفع جميع الفيديوهات
for v in videos:
    upload(v)
    time.sleep(8)
