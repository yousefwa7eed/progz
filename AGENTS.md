# AlmajidApp - Desktop Django Application

## Goal
تشغيل نظام Django كتطبيق ديسكتوب مستقل (بدون متصفح أو Python) عبر `pywebview` + `waitress`.

**آخر تحديث: الخميس 8 يوليو 2026 — إصلاحات أمان، قاعدة بيانات، جودة كود، واختبارات**

## Architecture
- `desktop_app.py` يشغّل خادم `waitress` WSGI على `127.0.0.1:8500` داخل thread
- `pywebview` يفتح نافذة أصلية (native window) متصلة بالخادم المحلي
- وسيط (middleware) `DownloadMiddleware` يعترض التحميلات ويحفظها في `%USERPROFILE%\Downloads`

## Key Files
- `D:\projects\ekhlas\desktop_app.py` - المُشغّل الرئيسي
- `D:\projects\ekhlas\config\settings.py` - إعدادات Django الأصلية
- `D:\projects\ekhlas\apps\utils\pdf_helpers.py` - دوال PDF المشتركة (ar, get_arabic_font)
- `D:\projects\ekhlas\apps\occasions\views.py` - كود التصدير (يستخدم pdf_helpers)
- `D:\projects\ekhlas\apps\beneficiaries\views.py` - تصدير PDF للمستفيدين (يستخدم pdf_helpers)
- `D:\projects\ekhlas\static\fonts\Amiri-Regular.ttf` - خط عربي مجاني مضمّن
- `D:\projects\ekhlas\static\fonts\Amiri-Bold.ttf` - خط عريان مجاني مضمّن
- `D:\projects\ekhlas\.env` - المتغيرات البيئية (ممنوع نشره)
- `D:\projects\ekhlas\requirements-pinned.txt` - قائمة الحزم بأرقام الإصدارات المثبتة
- `D:\projects\ekhlas\build.ps1` - سكربت بناء مؤتمت
- `D:\projects\ekhlas\dist\AlmajidApp\AlmajidApp.exe` - الملف التنفيذي النهائي
- `D:\projects\ekhlas\dist\AlmajidApp\_internal` - مجلد الاعتماديات (db.sqlite3, templates, static, apps/occasions/templates)

## Build Script (مستحسن)
```powershell
cd D:\projects\ekhlas
.\build.ps1
```

Or to skip tests:
```powershell
cd D:\projects\ekhlas
.\build.ps1 -SkipTests
```

## PyInstaller Build Command (يدوي)
```powershell
python -m PyInstaller --onedir --windowed --noconfirm --icon="static\images\icon.ico" --name="AlmajidApp" --add-data="templates;templates" --add-data="static;static" --add-data="media;media" --add-data="db.sqlite3;." --add-data="apps\occasions\templates;apps\occasions\templates" --add-data="static\fonts;static\fonts" --runtime-hook="rthook_importlib_metadata.py" --exclude-module=matplotlib --exclude-module=scipy --exclude-module=pandas --exclude-module=notebook --exclude-module=IPython --exclude-module=PyQt5 --hidden-import=pyotp --hidden-import=qrcode --hidden-import=openpyxl --hidden-import=fpdf --hidden-import=arabic_reshaper --hidden-import=bidi --hidden-import=apps.utils --copy-metadata="django-auditlog" desktop_app.py
```

## Runtime Hook (`rthook_importlib_metadata.py`)
ملف يُحقن قبل أي كود آخر في التطبيق المُجمّد لجعل `importlib.metadata` يجد حزم `dist-info` في `_internal/`:
```python
import sys, pathlib, importlib.metadata as _ilm
_internal = pathlib.Path(sys.executable).parent / '_internal'
sys.path.insert(0, str(_internal))
if _internal.is_dir():
    _orig_version = _ilm.version
    def _patched_version(name):
        try:
            return _orig_version(name)
        except _ilm.PackageNotFoundError:
            norm = name.lower().replace('-', '_')
            for _d in _internal.glob('*.dist-info'):
                pkg = _d.name.split('-')[0].lower().replace('-', '_')
                if pkg == norm:
                    return _ilm.PathDistribution(_d).version
            raise
    _ilm.version = _patched_version
```

## desktop_app.py Content
```python
import os
import sys
import json
import socket
import threading
import time
import re

# ── Load Supabase/DB config from external JSON file ──────────
def _load_db_config():
    config_paths = []
    if getattr(sys, 'frozen', False):
        config_paths.append(os.path.join(os.path.dirname(sys.executable), 'supabase_config.json'))
    else:
        config_paths.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'supabase_config.json'))
    for cfg_path in config_paths:
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, encoding='utf-8') as f:
                    cfg = json.load(f)
                db = cfg.get('database', {})
                if db.get('engine'):
                    os.environ['SUPABASE_DB_ENGINE']    = db['engine']
                    os.environ['SUPABASE_DB_HOST']      = db.get('host', '')
                    os.environ['SUPABASE_DB_PORT']      = str(db.get('port', 5432))
                    os.environ['SUPABASE_DB_NAME']      = db.get('name', 'postgres')
                    os.environ['SUPABASE_DB_USER']      = db.get('user', 'postgres')
                    os.environ['SUPABASE_DB_PASSWORD']  = db.get('password', '')
                    os.environ['SUPABASE_DB_SSLMODE']   = db.get('sslmode', 'require')
                    return True
            except Exception as e:
                print(f"Warning: Could not load DB config: {e}")
    return False

_using_supabase = _load_db_config()

# ── Ensure SECRET_KEY is set before Django loads ──────────────
if 'SECRET_KEY' not in os.environ:
    import secrets
    os.environ['SECRET_KEY'] = secrets.token_urlsafe(50)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

import django
import django.conf
settings = django.conf.settings

os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

# Force DEBUG off in frozen/production builds
if getattr(sys, 'frozen', False):
    settings.DEBUG = False

# Override paths when running frozen (EXE mode)
if getattr(sys, 'frozen', False):
    INTERNAL_DIR = os.path.join(os.path.dirname(sys.executable), '_internal')
    settings.TEMPLATES[0]['DIRS'] = [os.path.join(INTERNAL_DIR, 'templates')]
    settings.STATICFILES_DIRS = [os.path.join(INTERNAL_DIR, 'static')]
    settings.STATIC_ROOT = os.path.join(INTERNAL_DIR, 'staticfiles')
    if not _using_supabase:
        DATA_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'AlmajidApp', 'data')
        os.makedirs(DATA_DIR, exist_ok=True)
        DB_PATH = os.path.join(DATA_DIR, 'db.sqlite3')
        bundled_db = os.path.join(INTERNAL_DIR, 'db.sqlite3')
        if not os.path.exists(DB_PATH) and os.path.exists(bundled_db):
            import shutil
            shutil.copy2(bundled_db, DB_PATH)
        settings.DATABASES['default']['NAME'] = DB_PATH
        settings.DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

# Backup fix: add _internal to sys.path for importlib.metadata
if getattr(sys, 'frozen', False):
    _internal_path = os.path.join(os.path.dirname(sys.executable), '_internal')
    sys.path.insert(0, _internal_path)

django.setup()

# ── Run migrations automatically in frozen mode ──────────────
if getattr(sys, 'frozen', False):
    from django.core.management import call_command
    call_command('migrate', verbosity=0, interactive=False, run_syncdb=True)

# Force PyInstaller to pick up string-referenced modules
import whitenoise.middleware
import corsheaders.middleware
import allauth.account.middleware
import simple_history.middleware
import auditlog.middleware
import apps.audit.middleware
import apps.accounts.context_processors
import rest_framework_simplejwt.authentication
import django_filters.rest_framework
import rest_framework.schemas
import fpdf
import apps.utils.pdf_helpers

import psycopg2
import psycopg2.extensions

from django.core.wsgi import get_wsgi_application
django_app = get_wsgi_application()

# ── Download middleware for pywebview ──────────────────────────
DOWNLOAD_DIR = os.path.join(os.environ['USERPROFILE'], 'Downloads')

class DownloadMiddleware:
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        captured_body = []
        captured_status = [None]
        captured_headers = [None]

        def capturing_start(status, headers, exc_info=None):
            captured_status[0] = status
            captured_headers[0] = headers
            return captured_body.append

        app_iter = self.application(environ, capturing_start)
        body = b''.join(app_iter)
        if hasattr(app_iter, 'close'):
            app_iter.close()

        status = captured_status[0]
        headers = captured_headers[0]

        content_disposition = None
        for k, v in headers:
            if k.lower() == 'content-disposition':
                content_disposition = v
                break

        if content_disposition and 'attachment' in content_disposition:
            filename_match = re.search(r'filename="?([^";\n]+)"?', content_disposition)
            filename = filename_match.group(1) if filename_match else 'download'
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

            filepath = os.path.join(DOWNLOAD_DIR, filename)
            try:
                with open(filepath, 'wb') as f:
                    f.write(body)
                os.startfile(filepath)
                message = 'تم حفظ الملف في مجلد التحميلات: ' + filename
            except Exception as e:
                message = 'خطأ في حفظ الملف: ' + str(e)

            html = (
                '<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
                '<title>' + message + '</title>'
                '<style>'
                'body{font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:#f5f5f5}'
                '.card{background:#fff;padding:40px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.1);text-align:center;max-width:500px}'
                '.btn{display:inline-block;margin-top:20px;padding:10px 24px;background:#0d6efd;color:#fff;text-decoration:none;border-radius:6px;border:none;cursor:pointer;margin:4px}'
                '</style></head>'
                '<body><div class="card"><h3>' + message + '</h3>'
                '<button class="btn" onclick="window.history.back()">الرجوع</button>'
                '<button class="btn" onclick="window.close()" style="background:#6c757d">إغلاق النافذة</button>'
                '<script>setTimeout(function(){window.history.back()}, 3000)</script>'
                '</div></body></html>'
            )
            body = html.encode('utf-8')
            headers = [
                ('Content-Type', 'text/html; charset=utf-8'),
                ('Content-Length', str(len(body))),
            ]
            start_response('200 OK', headers)
            return [body]

        start_response(status, headers)
        return [body]

app = DownloadMiddleware(django_app)

HOST = '127.0.0.1'
PORT = 8500
BASE_URL = f'http://{HOST}:{PORT}'

import waitress
def start_server():
    try:
        waitress.serve(app, host=HOST, port=PORT, threads=8, _quiet=True)
    except Exception as e:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, f'خطأ في تشغيل الخادم:\n{e}', 'خطأ', 0)
        os._exit(1)

t = threading.Thread(target=start_server, daemon=True)
t.start()

for i in range(40):
    try:
        s = socket.create_connection((HOST, PORT), timeout=0.5)
        s.close()
        break
    except:
        if i == 0:
            print(f"Waiting for server on {HOST}:{PORT}...")
        time.sleep(0.5)
else:
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, 'تعذر تشغيل الخادم بعد 20 ثانية', 'خطأ', 0)
    os._exit(1)

import webview
window = webview.create_window(
    title='مؤسسة الماجد - الجهاز الاداري',
    url=BASE_URL,
    width=1280, height=800,
    resizable=True, fullscreen=False,
    min_size=(900, 600),
    easy_drag=False, confirm_close=True,
)
webview.start()
os._exit(0)
```

## Fixed Issues
1. ~~PDF Export - `FPDFUnicodeEncodingException`~~ **(تم الإصلاح)** تم تعديل الكود لاستخدام `apps/utils/pdf_helpers.py` مع خط Amiri المضمّن أو خط Windows كاحتياطي
2. ~~Startup crash - `importlib.metadata.PackageNotFoundError: django-auditlog`~~ **(تم الإصلاح)** تم إنشاء `rthook_importlib_metadata.py`
3. ~~Database bundled in EXE~~ **(تم الإصلاح)** تم نقل قاعدة البيانات إلى `%APPDATA%/AlmajidApp/data/` مع نسخ تلقائي من الملف المضمّن عند أول تشغيل
4. ~~SECRET_KEY ضعيف ومكشوف~~ **(تم الإصلاح)** تم توليد مفتاح عشوائي عند عدم وجوده، وإضافة `.env` مع إعدادات الإنتاج
5. ~~DEBUG=True في الإنتاج~~ **(تم الإصلاح)** إجبار `DEBUG=False` عند التشغيل من EXE
6. ~~Arabic unicode escapes~~ **(تم الإصلاح)** استبدال `\uXXXX` بنص عربي مباشر
7. ~~اختبارات صفرية~~ **(تم الإصلاح)** 20 اختباراً في 3 تطبيقات (accounts, beneficiaries, occasions)
8. **Excel Export** - يعمل بشكل صحيح عبر DownloadMiddleware

## Recent Changes (Session: CTO Review & Quality Improvements — يوليو 2026)
- **الأمان**: تم إصلاح SECRET_KEY (توليد عشوائي بدلاً من الثابت)، إجبار DEBUG=False في EXE، إنشاء `.env` مع key آمن
- **قاعدة البيانات**: نقل SQLite من `_internal/` إلى `%APPDATA%/AlmajidApp/data/` لضمان بقاء البيانات عند التحديث
- **الترحيل التلقائي**: إضافة `call_command('migrate')` في frozen mode لتطبيق تغييرات schema تلقائياً
- **إعادة هيكلة PDF**: استخراج دوال `ar()` و `get_arabic_font()` المشتركة إلى `apps/utils/pdf_helpers.py`
- **الخط العربي**: تضمين خط Amiri مفتوح المصدر في `static/fonts/` بدلاً من الاعتماد على خطوط Windows
- **Unicode escapes**: استبدال `\uXXXX` بنص عربي مباشر في desktop_app.py
- **سياسة كلمة المرور**: رفع الحد الأدنى من 4 إلى 8 أحرف مع تعقيد (حرف كبير، صغير، رقم، رمز)
- **الاختبارات**: 20 اختباراً جديداً في 3 تطبيقات (accounts, beneficiaries, occasions) — جميعها ناجحة
- **Timeout**: زيادة مهلة بدء الخادم من 10 إلى 20 ثانية مع رسالة خطأ للمستخدم
- **Build script**: إنشاء `build.ps1` مؤتمت يشمل اختبارات + ترحيز + بناء + تحقق
- **Dependencies**: إنشاء `requirements-pinned.txt` بأرقام إصدارات محددة
- **PyInstaller spec**: تحديث لتضمين fonts و apps.utils

### التغييرات السابقة (تغيير الملكية لمؤسسة الماجد)
- تم تغيير اسم التطبيق من "EkhlasApp" إلى "AlmajidApp"
- تم تغيير اسم المؤسسة من "جمعية الإخلاص الخيرية" إلى "مؤسسة الماجد"
- تم تغيير اسم النظام من "نظام الإدارة المتكامل" إلى "الجهاز الاداري"
- تم استبدال الشعار و icon.ico بالشعار الجديد
- تم إصلاح مشكلة تصدير PDF بالعربية في occasions/views.py
- تم تغيير البريد الإداري من admin@ekhlas.org.sa إلى admin@almajid.sa
- تم تحديث issuer الـ OTP من "الإخلاص" إلى "الماجد"

---

## Conversation History (Full Context)

ما يلي ملخص كامل للمحادثة التي دارت بين المستخدم والمساعد AI حتى لحظة إعداد هذا الملف. هذا السياق مهم لفهم ما يفكر فيه المستخدم وما تم إنجازه وما تبقى.

### البداية: تحويل Django إلى تطبيق ديسكتوب

طلب المستخدم تحويل مشروع Django (نظام جمعية الإخلاص الخيرية) إلى تطبيق ديسكتوب يعمل بدون متصفح أو Python، على شكل `.exe` واحد.

**المشكلة الأصلية**:
- التطبيق كان يعمل على `127.0.0.1:8000` كخادم Django عادي
- المستخدم كان يفتح المتصفح لاستخدامه
- يريد تطبيقاً مستقلاً

### الحل الأولي: `desktop_app.py`

تم إنشاء ملف `desktop_app.py` يستخدم:
1. `waitress.serve()` - خادم WSGI في thread منفصل على `127.0.0.1:8500`
2. `pywebview` - نافذة أصلية (native window) تتصل بالخادم المحلي
3. `os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'` - بدلاً من `settings.configure()`

### التطورات (حسب الترتيب الزمني)

#### 1. مشكلة الصور لا تظهر في الـ EXE
- تم حلها بإضافة `whitenoise` للتعامل مع الملفات الثابتة (static files)
- في الإعدادات (settings.py) تم إضافة المسارات الصحيحة

#### 2. مشكلة إعدادات Django (settings.configure vs settings module)
- في البداية كنا نستخدم `settings.configure()` مع تمرير القيم يدوياً
- هذا تسبب بفقدان إعدادات REST Framework, JWT, CORS, context processors إلخ
- **الحل**: استخدام `os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'` + `django.conf.settings` مباشرة
- هذا جعل كل الإعدادات الأصلية متاحة تلقائياً

#### 3. مشكلة صفحة المناسبات (TemplateDoesNotExist)
- صفحة المناسبات كانت ترجع خطأ 500 بعد البناء
- السبب: PyInstaller لا يجمّع ملفات HTML داخل مجلدات `apps/occasions/templates`
- **الحل**: إضافة `--add-data="apps\occasions\templates;apps\occasions\templates"` لأمر PyInstaller

#### 4. مشكلة أزرار التصدير (Download)
- أزرار "تصدير Excel / PDF" لم تكن تعمل لأن pywebview لا يدعم التحميلات
- **الحل**: إنشاء وسيط WSGI (DownloadMiddleware) في `desktop_app.py`
  - يعترض الاستجابات ذات `Content-Disposition: attachment`
  - يحفظ الملف في `%USERPROFILE%\Downloads`
  - يفتحه تلقائياً بالبرنامج الافتراضي (`os.startfile`)
  - يعرض صفحة HTML بالعربية تقول "تم حفظ الملف"

#### 5. مشكلة زر الإغلاق في صفحة نجاح التحميل
- المستخدم: "عند الانتهاء اضغط علي اغلاق للخروج من صفحه تم حفظ الملف لا يرجع"
- المشكلة: `window.close()` لا يعمل على الصفحات المفتوحة عادة (فقط النوافذ المنبثقة)
- **الحل**: استبدلنا `window.close()` بـ:
  - زر "الرجوع" → `window.history.back()`
  - زر "إغلاق النافذة" → `window.close()` (كخيار إضافي)
  - Auto-redirect بعد 3 ثوانٍ → `setTimeout(function(){window.history.back()}, 3000)`

#### 6. تغيير الجهاز (Computer Migration)
- المستخدم اضطر لتغيير جهاز الكمبيوتر
- **الحل** (السياق الحالي):
  - إنشاء ملف `AGENTS.md` هذا لحفظ كل السياق
  - إنشاء `requirements.txt` لتثبيت الحزم بسهولة
  - سيتم ضغط مجلد `D:\ekhlas` ونقله إلى الجهاز الجديد
  - على الجهاز الجديد: فك الضغط → `pip install -r requirements.txt` → إعادة بناء الـ EXE

### المشاكل المتبقية (لم تحل بعد)

1. ~~**PDF Export** - `FPDFUnicodeEncodingException`~~ **(تم الإصلاح)** استخدام `apps/utils/pdf_helpers.py` مع خط Amiri المضمّن
2. ~~**Arabic unicode escapes**~~ **(تم الإصلاح)** استبدال `\uXXXX` بنص عربي مباشر
3. ~~**SECRET_KEY ضعيف**~~ **(تم الإصلاح)** توليد عشوائي أو قراءة من `.env`
4. ~~**DEBUG=True في الإنتاج**~~ **(تم الإصلاح)** إجبار `False` في frozen mode
5. ~~**قاعدة البيانات داخل EXE**~~ **(تم الإصلاح)** نقل إلى `%APPDATA%/AlmajidApp/data/`
6. ~~**اختبارات صفرية**~~ **(تم الإصلاح)** 20 اختباراً في 3 تطبيقات
7. **إضافة features جديدة** → يتطلب إعادة بناء الـ EXE (مثال: إضافة اختبارات للتطبيقات الأخرى)

### ملاحظات فنية من المستخدم

- المستخدم يتحدث العربية، يفضل واجهة RTL (يمين لليسار)
- التطبيق يعمل على Windows فقط (pywebview + waitress + ctypes)
- اسم المشروع: "جمعية الإخلاص الخيرية - نظام الإدارة المتكامل"
- الـ EXE النهائي: `D:\ekhlas\dist\EkhlasApp\EkhlasApp.exe`
- مدة البناء: ~4 دقائق

### الـ EXE تم اختباره

- تسجيل الدخول → يعمل
- Dashboard → يعرض HTML طبيعي (30010 بايت)
- صفحة المناسبات → HTML (16546 بايت)
- المستفيدون → HTML (17221 بايت)
- المتبرعون → HTML (14823 بايت)
- الصور الثابتة → HTTP 200
- تصدير Excel → يعمل (تم اختباره: يحفظ الملف ويفتحه)
- جميع الصفحات ترجع محتوى مختلف وأكواد HTML سليمة
