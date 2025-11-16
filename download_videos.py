import gdown
import os

DOWNLOAD_FOLDER = "videos"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

FOLDER_URL = "https://drive.google.com/drive/folders/1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

print("⏳ جاري تحميل الفيديوهات من Google Drive...")
gdown.download_folder(url=FOLDER_URL, output=DOWNLOAD_FOLDER, use_cookies=False)
print(f"✅ تم تحميل جميع الفيديوهات في المجلد: {DOWNLOAD_FOLDER}")
