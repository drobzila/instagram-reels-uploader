import os
import json
import base64
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

def get_drive_service():
    b64 = os.environ.get("SERVICE_ACCOUNT_JSON_B64")
    if not b64:
        raise Exception("❌ SERVICE_ACCOUNT_JSON_B64 غير موجود")
    info = json.loads(base64.b64decode(b64))
    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)

def main():
    drive = get_drive_service()

    results = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
        fields="files(id, name)",
        pageSize=1000
    ).execute()

    files = results.get("files", [])
    print(f"عدد الملفات: {len(files)}")

    if not files:
        print("لا توجد فيديوهات.")
        return

    # كتابة الروابط في videos.txt مع وضع end-of-line المناسب
    with open("videos.txt", "w", encoding="utf-8", newline="\n") as f:
        for file in files:
            link = f"https://drive.google.com/uc?id={file['id']}"
            line = f"{link}  # {file['name']}"
            f.write(line + "\n")   # أضف "\n" صريح لكل سطر
            print(line)

    print("\n✅ تم حفظ الروابط في videos.txt")

if __name__ == "__main__":
    main()
