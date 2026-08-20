# Instagram Reels Uploader

أداة Python لأتمتة تنزيل الفيديوهات من Google Drive وتجهيزها ونشرها كـ Instagram Reels عبر Instagram Graph API.

## المميزات
- تنزيل الفيديوهات من Google Drive.
- رفع الفيديوهات إلى Instagram Reels.
- دعم Instagram Graph API وMeta access tokens.
- سكربتات مساعدة لتنزيل الفيديوهات وإدارة الملفات.

## المتطلبات
- حساب Instagram Professional مرتبط بصفحة Facebook.
- تطبيق Meta for Developers.
- صلاحيات Instagram Graph API المناسبة للنشر.
- Instagram User ID.
- وصول إلى Google Drive.
- Python والمتطلبات الموجودة في `requirements.txt`.

## التثبيت
```bash
git clone https://github.com/drobzila/instagram-reels-uploader.git
cd instagram-reels-uploader
pip install -r requirements.txt
```

## الإعداد
ضع بيانات API وAccess Tokens في متغيرات البيئة أو إعدادات محلية غير مرفوعة إلى Git.

**لا ترفع `session.json` أو Access Tokens أو Service Account credentials إلى مستودع عام.**

## التشغيل
```bash
python main.py
```

## البنية
- `main.py` — نقطة التشغيل الرئيسية.
- `download_drive_videos.py` — تنزيل الفيديوهات من Drive.
- `download_videos.py` — وظائف تنزيل إضافية.
- `upload_drive_to_mega.py` — نقل ملفات Drive إلى MEGA.
- `config.json` — إعدادات المشروع.
- `requirements.txt` — المتطلبات.

## ملاحظات
قد تحتاج عملية نشر Reels إلى إعدادات وصلاحيات Meta صحيحة، بالإضافة إلى أن يكون الفيديو متاحًا للمعالجة وفق متطلبات Instagram.

## الترخيص
لم يتم تحديد ترخيص للمشروع بعد.
