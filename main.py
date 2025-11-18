import os
import gdown
from instagrapi import Client

# -----------------------------
# 1. Load IG session
# -----------------------------
def load_session():
    cl = Client()
    if os.path.exists("session.json"):
        cl.load_settings("session.json")
        cl.login_by_sessionid(cl.get_settings()["authorization_data"]["sessionid"])
    else:
        raise Exception("session.json غير موجود!")
    return cl


# -----------------------------
# 2. Extract video ID from Google Drive link
# -----------------------------
def extract_drive_id(url: str) -> str:
    if "id=" in url:
        return url.split("id=")[1]
    if "/d/" in url:
        return url.split("/d/")[1].split("/")[0]
    raise ValueError("رابط Google Drive غير صحيح")


# -----------------------------
# 3. Download video using gdown
# -----------------------------
def download_video(url: str, output_folder="downloads"):
    os.makedirs(output_folder, exist_ok=True)
    file_id = extract_drive_id(url)
    output_path = os.path.join(output_folder, file_id + ".mp4")
    gdown.download(f"https://drive.google.com/uc?id={file_id}", output_path, quiet=False)
    return output_path


# -----------------------------
# 4. Read links.txt
# -----------------------------
def load_links():
    with open("links.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# -----------------------------
# 5. Upload video to Instagram Reels
# -----------------------------
def upload_reel(cl, video_path):
    cl.clip_upload(
        video_path,
        caption="تم النشر تلقائيًا ✓"
    )
    print(f"نُشر على إنستغرام → {video_path}")


# -----------------------------
# 6. Main logic
# -----------------------------
def main():
    print("تحميل session…")
    cl = load_session()

    print("قراءة links.txt…")
    links = load_links()

    print("بدء تحميل الفيديوهات…")
    for link in links:
        print(f"تحميل: {link}")
        video_file = download_video(link)

        print("رفع إلى إنستغرام…")
        upload_reel(cl, video_file)

    print("اكتمل السكربت ✓")


if __name__ == "__main__":
    main()
