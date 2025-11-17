import os
import requests
import time

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]

# ضع هنا اسم صاحب المستودع واسم الريبو مباشرة
OWNER = "drobliza"
REPO = "instagram-reels-uploader"

def get_videos_from_latest_release():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
    r = requests.get(url).json()

    videos = [
        a["browser_download_url"]
        for a in r.get("assets", [])
        if a["name"].endswith(".mp4")
    ]

    if not videos:
        print("❌ لم يتم العثور على أي فيديوهات في أحدث Release.")
        exit(1)

    print("🎥 الفيديوهات الموجودة في Release:")
    for v in videos:
        print(" -", v)

    return videos

def upload_reel(video_url):
    print(f"🎬 رفع الفيديو: {video_url}")

    # 1) إنشاء الريلز (Container)
    container = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": "Uploaded automatically 🤖",
            "access_token": ACCESS_TOKEN
        }
    ).json()

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

    print("✅ تم النشر:", publish)

def main():
    videos = get_videos_from_latest_release()
    for video_url in videos:
        upload_reel(video_url)
        time.sleep(10)  # فاصل بسيط بين الفيديوهات

if __name__ == "__main__":
    main()
