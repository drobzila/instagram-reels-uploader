"""
Instagram Reels Uploader
-----------------------
وظيفة:
- تنزيل فيديوهات من Google Drive (مجلد محدد)
- جعلها قابلة للوصول public (أي anyoneWithLink)
- إنشاء container على Instagram عبر Graph API باستخدام video_url من Drive
- نشرها كـ Reels عبر media_publish

ملاحظات مهمة:
- ضع service account JSON كـ service_account.json في نفس المجلد أو غيّر المسار.
- استخدم متغيرات البيئة التالية:
    - IG_USER_ID      => Instagram Business Account ID (مثل 1784...)
    - ACCESS_TOKEN    => Long-Lived Access Token (لا تضعه في الكود)
    - GOOGLE_APPLICATION_CREDENTIALS => مسار ملف service account JSON (اختياري)
"""

import os
import io
import json
import time
import random
import logging
import datetime
import pathlib
import requests

from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env إن وُجد (اختياري)
load_dotenv()

# إعداد اللوق
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# تحميل الإعدادات من config.json
with open("config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

FOLDER_ID = cfg.get("FOLDER_ID")
UPLOAD_LIMIT = cfg.get("UPLOAD_LIMIT_PER_RUN", 5)
SCHEDULE_TIMES = cfg.get("SCHEDULE_TIMES", [7,10,12,16,21])
VIDEO_TITLES = cfg.get("VIDEO_TITLES", [])
LOG_FILE = cfg.get("LOG_FILE", "upload_log.txt")
TEMP_DIR = pathlib.Path(cfg.get("TEMP_DOWNLOAD_DIR", "temp_videos"))
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# قيم يجب تعريفها عبر متغيرات البيئة
IG_USER_ID = os.getenv("IG_USER_ID")            # يجب وضعه كـ env
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")        # يجب وضعه كـ env

if not IG_USER_ID or not ACCESS_TOKEN:
    logging.error("Please set IG_USER_ID and ACCESS_TOKEN as environment variables.")
    raise SystemExit("Missing required environment variables.")

# تهيئة Google Drive service عبر Service Account JSON
# ضع ملف service_account.json في نفس المجلد أو اضبط GOOGLE_APPLICATION_CREDENTIALS env var.
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")

SCOPES = ["https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials, cache_discovery=False)

# ---------------------------
# دوال مساعدة
# ---------------------------
def make_unique_title(original_name):
    # توليد عنوان فريد من القائمة أو اسم الملف
    if VIDEO_TITLES:
        attempts = 0
        while attempts < 20:
            t = random.choice(VIDEO_TITLES)
            if not is_already_uploaded(t):
                return t
            attempts += 1
    # fallback: استخدم اسم الملف مع طابع زمني
    base = os.path.splitext(original_name)[0]
    return f"{base} - {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

def is_already_uploaded(title):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return title in f.read()

def log_upload(original_name, ig_media_id, caption, scheduled_time):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat()} | {original_name} | {ig_media_id} | {scheduled_time} | {caption}\n")

# ---------------------------
# Google Drive: تحميل الملف محليًا وإعطاؤه صلاحية anyoneWithLink
# ---------------------------
def make_file_public(file_id):
    try:
        drive_service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
            fields="id"
        ).execute()
    except Exception as e:
        # أحيانًا يظهر خطأ لو الصلاحية موجودة مسبقًا — تجاهله
        logging.debug(f"permission create: {e}")

def download_file_to_local(file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    local_path = TEMP_DIR / file_name
    fh = io.FileIO(local_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            logging.info(f"Download {file_name}: {int(status.progress() * 100)}%")
    logging.info(f"Downloaded {file_name} -> {local_path}")
    return str(local_path)

def make_drive_public_url(file_id):
    # رابط مباشر صالح عادةً لملفات Drive:
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# ---------------------------
# Instagram: رفع ونشر الريل
# وثائق مرجعية: https://developers.facebook.com/docs/instagram-platform/content-publishing/
# ---------------------------
GRAPH_API_BASE = "https://graph.facebook.com/v20.0"

def create_ig_container(video_url, caption):
    """
    ينشئ container للفيديو (نوع REELS)
    يرجع creation_id عند النجاح
    """
    endpoint = f"{GRAPH_API_BASE}/{IG_USER_ID}/media"
    params = {
        "media_type": "REELS",   # حسب توثيق Meta: استخدم REELS لعمل Reel
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    resp = requests.post(endpoint, data=params)
    if resp.status_code != 200:
        logging.error("Failed to create container: %s", resp.text)
        return None, resp.text
    data = resp.json()
    creation_id = data.get("id") or data.get("container_id")
    logging.info(f"Created IG media container: {creation_id}")
    return creation_id, None

def publish_ig_container(creation_id):
    endpoint = f"{GRAPH_API_BASE}/{IG_USER_ID}/media_publish"
    params = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }
    resp = requests.post(endpoint, data=params)
    if resp.status_code != 200:
        logging.error("Failed to publish media: %s", resp.text)
        return None, resp.text
    data = resp.json()
    media_id = data.get("id")
    logging.info(f"Published IG media id: {media_id}")
    return media_id, None

# ---------------------------
# منطق التشغيل الرئيسي
# ---------------------------
def main():
    logging.info("Starting Instagram Reels uploader")

    # الحصول على ملفات الفيديو من Drive
    q = f"'{FOLDER_ID}' in parents and mimeType contains 'video/'"
    res = drive_service.files().list(q=q, fields="files(id,name,mimeType)").execute()
    files = res.get("files", [])
    if not files:
        logging.warning("No video files found in Drive folder.")
        return

    # اختر عشوائياً وحتى UPLOAD_LIMIT
    random.shuffle(files)
    selected = files[:UPLOAD_LIMIT]

    # تحديد أوقات النشر اليوم (قابلة للتعديل)
    tz = datetime.timezone(datetime.timedelta(hours=1))  # الجزائر +1 (عدّل إن لزم)
    today = datetime.date.today()
    schedule_datetimes = []
    for h in SCHEDULE_TIMES[:len(selected)]:
        schedule_datetimes.append(datetime.datetime.combine(today, datetime.time(h,0), tzinfo=tz))

    for file, sched_dt in zip(selected, schedule_datetimes):
        file_id = file["id"]
        orig_name = file["name"]

        # توليد عنوان/وصف
        title = make_unique_title(orig_name)
        caption = f"{title}\n\nاستمع إلى تلاوة مؤثرة. #قرآن #تلاوة"

        if is_already_uploaded(title):
            logging.info(f"Title already uploaded, skipping: {title}")
            continue

        # 1) جعل الملف public على Drive
        make_file_public(file_id)

        # 2) تنزيل الملف محليًا (اختياري؛ ليس ضروريًا لو اعتمدت على video_url المباشر)
        local_path = download_file_to_local(file_id, orig_name)

        # 3) الحصول على رابط مباشر لـ Google Drive (يستخدمه Graph API لسحب الفيديو)
        video_url = make_drive_public_url(file_id)
        logging.info(f"Using video_url: {video_url}")

        # 4) إذا أردت الجدولة: ننتظر حتى وقت النشر ثم نرفع
        now = datetime.datetime.now(tz)
        if sched_dt > now:
            wait_seconds = (sched_dt - now).total_seconds()
            logging.info(f"Scheduled at {sched_dt.isoformat()} — waiting {int(wait_seconds)} seconds before publishing.")
            # ملاحظة: هذا سيجعل السكربت ينتظر (بدون جدولة خارجية)
            time.sleep(wait_seconds)

        # 5) إنشاء الـ container على Instagram
        creation_id, err = create_ig_container(video_url, caption)
        if not creation_id:
            logging.error(f"Failed to create container for {orig_name}: {err}")
            continue

        # 6) تنفيذ النشر
        media_id, err = publish_ig_container(creation_id)
        if not media_id:
            logging.error(f"Failed to publish for {orig_name}: {err}")
            continue

        # 7) تسجيل النجاح وحذف الملف المحلي المؤقت
        log_upload(orig_name, media_id, caption, sched_dt.isoformat())
        try:
            os.remove(local_path)
            logging.info(f"Deleted temporary file {local_path}")
        except Exception as e:
            logging.debug(f"Could not delete temp file: {e}")

    logging.info("Run completed.")

if __name__ == "__main__":
    main()
