# راهنمای کامل دیپلوی (فارسی) — پنل X4G روی Railway

## گام ۱ — ساخت ریپازیتوری در گیت‌هاب
1. وارد github.com شوید → **New repository**
2. یک اسم بدید (مثلاً `x4g-panel`) → Private یا Public، فرقی نمی‌کند
3. این ۵ فایل را در ریشه‌ی ریپو آپلود/کامیت کنید:
   - `Dockerfile`
   - `nginx.conf.template`
   - `start.sh`
   - `sub-view.html`
   - `README.md`

> نکته: چون این ریپو یک "فورک منطقی" از پروژه‌ی Heimdall است (فقط فایل‌های دیپلوی خودتان را دارید، نه کد اصلی x-ui)، لازم نیست کل ریپوی sh7CBAC/Heimdall را فورک کنید — Dockerfile در زمان build خودش باینری release را از گیت‌هاب دانلود می‌کند.

## گام ۲ — اتصال به Railway (برای کمترین پینگ)
1. برو به https://railway.com → لاگین با گیت‌هاب
2. **New Project → Deploy from GitHub repo** → ریپوی بالا را انتخاب کن
3. **مهم برای پینگ پایین:** قبل یا بعد از دیپلوی، در تنظیمات پروژه دنبال گزینه‌ی **Region** بگرد (در Settings سرویس). برای کاربر ایران، این ترتیب معمولاً بهترین پینگ را می‌دهد:
   - `europe-west4` (هلند) — معمولاً بهترین گزینه
   - `asia-southeast1` (سنگاپور) — گزینه‌ی دوم خوب
   - از `us-west`/`us-east` بپرهیز، پینگ بالا می‌آورد
4. صبر کن تا Build و Deploy تمام شود (چند دقیقه — دانلود باینری Heimdall انجام می‌شود)
5. برو به **Settings → Networking → Generate Domain**
6. **Target Port را روی `3000` تنظیم کن** (چون nginx دقیقاً همین پورت ثابت را گوش می‌دهد — طبق `start.sh`)
7. (اختیاری ولی توصیه‌شده) برو به **Volumes → Add Volume** و مسیر `/etc/x-ui` را وصل کن تا با هر ریدیپلوی، تنظیمات و کاربرها پاک نشوند

## گام ۳ — اولین ورود
آدرس زیر را باز کن:
```
https://YOUR-APP.up.railway.app/managepanel/
```
یوزر/پسورد پیش‌فرض: `admin` / `admin` → **فوری از داخل پنل عوضش کن**.

## گام ۴ — ساخت اینباند (دستی)
| فیلد | مقدار |
|---|---|
| Protocol | VLESS |
| Listen Port | `8080` (ثابت، تغییر ندهید) |
| Network | ws |
| Security | none |
| Path | مثلاً `/cdn` |

یا این مرحله را با اسکریپت `auto_config.py` خودکار کن (پایین توضیح داده شده).

## گام ۵ — لینک کلاینت
```
vless://UUID@YOUR-APP.up.railway.app:443?encryption=none&security=tls&sni=YOUR-APP.up.railway.app&fp=chrome&type=ws&host=YOUR-APP.up.railway.app&path=%2Fcdn#MyConfig
```

## گام ۶ — لینک ساب (اشتراک)
```
https://YOUR-APP.up.railway.app/sub/USER_SUB_ID
```
باز کردنش توی مرورگر → صفحه‌ی زیبای QR/کپی نشان می‌دهد.
باز کردنش توی اپ کلاینت (v2rayNG، Streisand، Hiddify و…) → مستقیم متن ساب می‌دهد.

---

## خودکارسازی گام ۴ با اسکریپت (اختیاری)

بعد از این‌که دیپلوی انجام شد و پسورد پنل را عوض کردید:

```bash
pip install requests
python3 auto_config.py \
  --base-url https://YOUR-APP.up.railway.app \
  --username admin \
  --password YOUR_NEW_PASSWORD \
  --ws-path /cdn \
  --remark MyConfig
```

خروجی، لینک VLESS آماده برای کلاینت را چاپ می‌کند — دیگر نیازی نیست دستی توی پنل کلیک کنید.

> اگر URL و یوزرنیم/پسورد جدید پنل را برام بفرستید، همین اسکریپت را من مستقیم توی sandbox برایتان اجرا می‌کنم و لینک نهایی را تحویل می‌دهم.
