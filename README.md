# Instagram Reels Uploader

سكريبت Python يحمّل فيديوهات من Google Drive وينشرها كـ Instagram Reels عبر Instagram Graph API.

## متطلبات سابقة
1. Instagram Professional (Business أو Creator) مرتبط بصفحة Facebook.  
2. تطبيق على Meta for Developers مع الأذونات:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
3. Access Token طويل المدى (Long-Lived Access Token).
4. Instagram Business Account ID (`IG_USER_ID`).
5. Service account JSON للوصول إلى Google Drive (أو طريقة وصول بديلة).

**مراجع رسمية:**  
- توثيق نشر المحتوى (Reels) — Meta / Instagram Graph API. :contentReference[oaicite:0]{index=0}

## إعداد المتغيرات
ضع القيم الحساسة في متغيرات بيئة (أو ملف `.env`):

