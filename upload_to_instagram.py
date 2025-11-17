import os
import json
import base64
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from tqdm import tqdm

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

# Google Drive folder ID
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

# Decode Base64 service account JSON
encoded = os.getenv("SERVICE_ACCOUNT_JSON_B64")
service_account_info = json.loads(base64.b64decode(encoded))

creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)

drive_service = build("drive", "v3", credentials=creds)


def get_drive_videos(folder_id):
    query = f"'{folder_id}' in parents and mimeType contains 'video/'"
    results = drive_service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()
    return results.get("files", [])


def download_file(file_id, filename):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {"Authorization": f"Bearer {creds.token}"}

    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))

    with open(filename, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as bar:
        for chunk in response.iter_content(1024 * 1024):
            f.write(chunk)
            bar.update(len(chunk))

    return filename


def upload_instagram_video(video_path):
    print("Uploading:", video_path)

    create_url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media"

    res = requests.post(create_url, data={
        "media_type": "REELS",
        "caption": "Uploaded automatically 🤖",
        "access_token": ACCESS_TOKEN,
        "upload_phase": "start"
    })

    print("Create session:", res.text)
    return None  # هذا الجزء لاحقًا سنضبطه، حسب API النهائي


def main():
    files = get_drive_videos(FOLDER_ID)

    if not files:
        print("❌ No videos found in the folder.")
        return

    for f in files:
        filename = f["name"]
        print(f"⬇️ Downloading {filename}...")
        download_file(f["id"], filename)

        # هنا رفع الفيديو
        upload_instagram_video(filename)

        os.remove(filename)
        print(f"🗑️ Deleted: {filename}")


if __name__ == "__main__":
    main()
