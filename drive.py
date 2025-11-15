import os
import json
import base64
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"  # ضع مجلدك هنا

def get_drive_service():
    service_account_b64 = os.getenv("SERVICE_ACCOUNT_JSON_B64")
    service_account_json = base64.b64decode(service_account_b64)
    info = json.loads(service_account_json)

    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)

def main():
    drive = get_drive_service()

    results = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])
    print(f"عدد الملفات: {len(files)}")

    links = []
    for f in files:
        link = f"https://drive.google.com/uc?id={f['id']}"
        print(link, "#", f["name"])
        links.append({
            "name": f["name"],
            "url": link
        })

    with open("videos.json", "w", encoding="utf8") as out:
        json.dump(links, out, ensure_ascii=False, indent=2)

    print("تم إنشاء videos.json")

if __name__ == "__main__":
    main()
