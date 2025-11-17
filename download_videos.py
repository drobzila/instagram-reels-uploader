import os
import gdown

# مجلد حفظ الفيديوهات
DOWNLOAD_FOLDER = "videos"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ضع هنا Google Drive folder ID
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

print("⏳ جاري تحميل الفيديوهات من Google Drive...")

gdown.download_folder(
    id=FOLDER_ID,
    output=DOWNLOAD_FOLDER,
    quiet=False,
    use_cookies=False
)

print(f"✅ تم تحميل جميع الفيديوهات في المجلد: {DOWNLOAD_FOLDER}")
