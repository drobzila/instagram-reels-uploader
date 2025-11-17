import os
import json
import base64
import requests
import math
from google.oauth2 import service_account
from googleapiclient.discovery import build

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

# Decode service account
encoded = os.getenv("SERVICE_ACCOUNT_JSON_B64")
service_info = json.loads(base64.b64decode(encoded))

creds = service_account.Credentials.from_service_account_info(
    service_info,
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)
drive = build("drive", "v3", credentials=creds)

def get_videos(folder_id):
    q = f"'{folder_id}' in parents and mimeType contains 'video/'"
    r = drive.files().list(q=q, fields="files(id,name)").execute()
    return r.get("files", [])


def download(file_id, name):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {"Authorization": f"Bearer {creds.token}"}
    r = requests.get(url, headers=headers)

    with open(name, "wb") as f:
        f.write(r.content)

    return name


def upload_reel(local_path):
    file_size = os.path.getsize(local_path)

    # 1️⃣ Start
    start_res = requests.post(
        f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media",
        data={
            "media_type": "REELS",
            "upload_phase": "start",
            "file_size": file_size,
            "access_token": ACCESS_TOKEN
        }
    ).json()
    print("START:", start_res)

    session_id = start_res["upload_session_id"]
    upload_url = start_res["upload_url"]

    # 2️⃣ Transfer (chunked upload)
    chunk_size = 1024 * 1024 * 4   # 4MB
    with open(local_path, "rb") as f:
        chunk_index = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            transfer_res = requests.post(
                upload_url,
                data={
                    "upload_phase": "transfer",
                    "start_offset": chunk_index,
                    "access_token": ACCESS_TOKEN
                },
                files={"video_file_chunk": chunk}
            ).json()

            print("CHUNK:", transfer_res)

            chunk_index = transfer_res["end_offset"]

    # 3️⃣ Finish
    finish_res = requests.post(
        f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media",
        data={
            "upload_phase": "finish",
            "upload_session_id": session_id,
            "access_token": ACCESS_TOKEN,
            "caption": "Uploaded automatically 🤖"
        }
    ).json()

    print("FINISH:", finish_res)

    return finish_res


def main():
    videos = get_videos(FOLDER_ID)
    if not videos:
        print("❌ No videos found!")
        return

    for v in videos:
        print("Downloading:", v["name"])
        path = download(v["id"], v["name"])

        print("Uploading to Instagram…")
        upload_reel(path)

        os.remove(path)
        print("Deleted:", path)


if __name__ == "__main__":
    main()
