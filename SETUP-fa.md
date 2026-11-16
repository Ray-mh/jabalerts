<div dir="rtl">

# راهنمای راه‌اندازی Job Radar

حدود ۴۵ دقیقه طول می‌کشه. به ترتیب جلو برو. هر جا «📋 یادداشت کن» دیدی، اون مقدار رو یه جا نگه دار، چون در مرحله‌ی ۶ لازمش داری.

---

## ۱. یک Gmail جدید فقط برای هشدارها

1. یک اکانت Gmail جدید بساز (مثلاً `ray.jobalerts@gmail.com`).
2. توی همون اکانت برو به **Google Account → Security** و **2-Step Verification** رو روشن کن.
3. برو به صفحه‌ی **myaccount.google.com/apppasswords**، یک اسم بنویس (مثلاً `job-radar`) و **Create** رو بزن.
4. رمز ۱۶ حرفی‌ای که نشون می‌ده رو 📋 یادداشت کن. این همون `GMAIL_APP_PASSWORD` هست.

## ۲. ساختن هشدارهای شغلی

همه‌ی هشدارها باید به همین Gmail جدید برسن. هر جا گزینه‌ی تناوب (frequency) بود، **سریع‌ترین گزینه** رو انتخاب کن (مثلاً «as soon as posted» یا «daily»).

**دکترا: AcademicTransfer** (تقریباً همه‌ی دانشگاه‌های هلند اینجا آگهی می‌ذارن)
- با ایمیل جدید یک اکانت بساز و چند **Job alert** تعریف کن. مثلاً:
  - کلمه‌ی کلیدی `PhD` به‌همراه حوزه‌هایی مثل design، visual communication، architecture، heritage، media، humanities
  - یا کلمات کلیدی جدا: `PhD design`، `PhD visual`، `PhD illustration`، `PhD architecture`
- اختیاری: در **EURAXESS** هم هشدار بساز (کشور: Netherlands، Research profile: First Stage Researcher (R1)).

**لینکدین**
- در لینکدین جست‌وجو کن (مثلاً `graphic designer`، `visual designer`، `UX/UI designer`، `illustrator`، با Location: Netherlands) و **Set alert** رو روشن کن.
- لینکدین هشدارها رو به ایمیل اکانت لینکدینت می‌فرسته. پس یکی از این دو کار رو بکن:
  - در ایمیل اصلی‌ات یک **قانون فوروارد خودکار** بساز که ایمیل‌های `jobalerts-noreply@linkedin.com` رو به Gmail جدید بفرسته (Gmail: Settings → Filters → Forward to؛ Outlook: Rules)،
  - یا Gmail جدید رو به‌عنوان ایمیل دوم به لینکدین اضافه کن و اونو Primary کن.
- برای سرعت بیشتر، اعلان‌های اپ لینکدین روی گوشی رو هم روشن نگه دار.

**Indeed**
- در nl.indeed.com جست‌وجو کن و هشدار شغلی (Job alert) بساز. ایمیلی که وارد می‌کنی **Gmail جدید** باشه.

## ۳. ربات تلگرام

1. در تلگرام به **@BotFather** پیام بده، `/newbot` رو بفرست و یک اسم انتخاب کن.
2. توکنی که بهت می‌ده رو 📋 یادداشت کن. این `TELEGRAM_BOT_TOKEN` هست.
3. ربات جدیدت رو باز کن و یک پیام (مثلاً `سلام`) بهش بفرست.
4. توی مرورگر این آدرس رو باز کن، و به‌جای TOKEN توکن خودت رو بذار:
   `https://api.telegram.org/botTOKEN/getUpdates`
5. عددی که جلوی `"chat":{"id":` نوشته رو 📋 یادداشت کن. این `TELEGRAM_CHAT_ID` هست.

## ۴. کلید API هوش مصنوعی (Claude)

1. در **console.anthropic.com** ثبت‌نام کن و از بخش **Billing** کمی اعتبار اضافه کن (مثلاً ۱۰ دلار).
2. در **Limits** یک سقف ماهانه بذار (مثلاً ۱۰ دلار) تا هیچ‌وقت بیشتر از اون خرج نشه.
3. از **API Keys → Create Key** یک کلید بساز و 📋 یادداشت کن. این `ANTHROPIC_API_KEY` هست.

## ۵. ریپو

فایل‌ها از قبل در ریپوی `Ray-mh/jabalerts` هستن. ریپو باید **Public** باشه، چون GitHub Pages رایگان فقط روی ریپوی عمومی کار می‌کنه. سی‌وی و رمزهات داخل ریپو نیستن و فقط در Secrets ذخیره می‌شن.

## ۶. وارد کردن رمزها (Secrets)

در ریپو برو به **Settings → Secrets and variables → Actions → New repository secret** و این شش مورد رو یکی‌یکی بساز:

| اسم Secret | مقدار |
|---|---|
| `GMAIL_ADDRESS` | آدرس Gmail جدید |
| `GMAIL_APP_PASSWORD` | رمز ۱۶ حرفی مرحله‌ی ۱ |
| `ANTHROPIC_API_KEY` | کلید مرحله‌ی ۴ |
| `TELEGRAM_BOT_TOKEN` | توکن ربات |
| `TELEGRAM_CHAT_ID` | عدد chat id |
| `CV_PROFILE` | کل متن فایل `cv-profile.txt` (از کنار این پوشه) |

هر وقت سی‌وی‌ات عوض شد، فقط `CV_PROFILE` رو آپدیت کن.

## ۷. روشن کردن سایت

**Settings → Pages**: بخش Source رو بذار روی **Deploy from a branch**، Branch رو **main** و پوشه رو **/docs** انتخاب کن، بعد **Save** رو بزن.
چند دقیقه بعد سایتت روی `https://ray-mh.github.io/jabalerts/` بالا میاد.

## ۸. تست

1. برو به تب **Actions** و اگه پرسید، Actions رو فعال کن.
2. **Test Telegram** رو انتخاب کن، **Run workflow** رو بزن و صبر کن. باید پیام «✅ Job Radar وصل شد!» توی تلگرام بیاد.
3. بعد **Check job alerts** رو باز کن و **Run workflow** رو بزن. اگه هشداری توی ایمیل باشه، نتیجه‌ها توی سایت و تلگرام میان.
4. اگه چیزی قرمز شد (❌)، روی اون اجرا بزن، متن خطا رو کپی کن و برای Claude بفرست.

## ۹. اجرای هر ۱۰ دقیقه (cron-job.org)

زمان‌بند خود GitHub ممکنه تا نیم ساعت عقب بیفته. برای همین یک سرویس رایگان بیرونی هر ۱۰ دقیقه ریپو رو بیدار می‌کنه. (اگه این مرحله رو انجام ندی، سیستم باز هم کار می‌کنه، فقط حدوداً هر ۳۰ دقیقه.)

**الف) توکن GitHub**
1. **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**
2. Repository access: **Only select repositories** و `jabalerts` رو انتخاب کن.
3. Permissions: **Actions → Read and write**
4. Expiration: حداکثر (یک سال). توکن رو 📋 یادداشت کن.

**ب) cron-job.org**
1. ثبت‌نام کن و روی **Create cronjob** بزن.
2. **URL** (به‌جای USERNAME اسم کاربری GitHub خودت رو بذار):
   `https://api.github.com/repos/Ray-mh/jabalerts/actions/workflows/check.yml/dispatches`
3. **Schedule:** Every 10 minutes
4. در **Advanced**:
   - Request method: **POST**
   - Headers:
     - `Authorization` = `Bearer` و بعد یک فاصله و توکنت
     - `Accept` = `application/vnd.github+json`
     - `User-Agent` = `job-radar`
   - Request body: `{"ref":"main"}`
5. ذخیره کن و **Test run** رو بزن. جواب `204` یعنی همه‌چیز درسته.

یک سال بعد توکن منقضی می‌شه و باید یک توکن تازه بسازی و در cron-job.org جایگزینش کنی.

---

## تنظیمات (فایل `config.json`)

| تنظیم | معنی |
|---|---|
| `threshold` | حداقل امتیاز برای شغل‌های لینکدین و Indeed (۷۰) |
| `phd_threshold` | حداقل امتیاز برای دکترا (۷۰) |
| `notify_dutch_required` | اگه `false` باشه، شغل‌های 🔴 به تلگرام فرستاده نمی‌شن (ولی توی سایت می‌مونن) |
| `reason_language` | زبان توضیح تطابق (`Persian` یا `English`) |

## چند نکته‌ی مهم

- **سرعت:** سیستم هر ۱۰ دقیقه ایمیل رو چک می‌کنه، ولی خود هشدار باید اول از لینکدین، Indeed یا AcademicTransfer برسه. پس سرعت نهایی به سرعت ایمیل‌های اون سایت‌ها هم بستگی داره.
- **لینکدین:** ایمیل‌هاش معمولاً فقط عنوان، شرکت و شهر رو دارن. برای همین امتیاز این شغل‌ها با برچسب «Scored from title» مشخص شده و دقتش کمتره. برای آگهی‌های آکادمیک، متن کامل آگهی خونده می‌شه.
- **حریم خصوصی:** لیست شغل‌ها روی سایت عمومیه (موتورهای جست‌وجو ایندکسش نمی‌کنن)، ولی سی‌وی و رمزهات فقط در Secrets هستن و دیده نمی‌شن.
- **هزینه:** GitHub، تلگرام و cron-job.org رایگانن. فقط Claude هزینه داره، که برای چند ده آگهی در روز معمولاً چند دلار در ماهه، و با سقفی که در مرحله‌ی ۴ گذاشتی کنترل می‌شه.

</div>
