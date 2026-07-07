# AlmajidApp - Desktop Django Application

## Goal
تشغيل نظام Django كتطبيق ديسكتوب مستقل (بدون متصفح أو Python) عبر `pywebview` + `waitress`.

**آخر تحديث: تم تغيير الملكية من "جمعية الإخلاص الخيرية" إلى "مؤسسة الماجد".**

## Architecture
- `desktop_app.py` يشغّل خادم `waitress` WSGI على `127.0.0.1:8500` داخل thread
- `pywebview` يفتح نافذة أصلية (native window) متصلة بالخادم المحلي
- وسيط (middleware) `DownloadMiddleware` يعترض التحميلات ويحفظها في `%USERPROFILE%\Downloads`

## Key Files
- `D:\projects\ekhlas\desktop_app.py` - المُشغّل الرئيسي
- `D:\projects\ekhlas\config\settings.py` - إعدادات Django الأصلية
- `D:\projects\ekhlas\apps\occasions\views.py` - كود التصدير (PDF تم إصلاح مشكلة العربية)
- `D:\projects\ekhlas\apps\beneficiaries\views.py` - تصدير PDF للمستفيدين
- `D:\projects\ekhlas\dist\AlmajidApp\AlmajidApp.exe` - الملف التنفيذي النهائي
- `D:\projects\ekhlas\dist\AlmajidApp\_internal` - مجلد الاعتماديات (db.sqlite3, templates, static, apps/occasions/templates)

## PyInstaller Build Command
```powershell
python -m PyInstaller --onedir --windowed --noconfirm --icon="static\images\icon.ico" --name="AlmajidApp" --add-data="templates;templates" --add-data="static;static" --add-data="media;media" --add-data="db.sqlite3;." --add-data="apps\occasions\templates;apps\occasions\templates" --runtime-hook="rthook_importlib_metadata.py" --exclude-module=matplotlib --exclude-module=scipy --exclude-module=pandas --exclude-module=notebook --exclude-module=IPython --exclude-module=PyQt5 --hidden-import=pyotp --hidden-import=qrcode --hidden-import=openpyxl --hidden-import=fpdf --hidden-import=arabic_reshaper --hidden-import=bidi --copy-metadata="django-auditlog" desktop_app.py
```

**ملاحظة**: يجب تشغيل الأمر من داخل مجلد `D:\projects\ekhlas`.

## ## Runtime Hook (`rthook_importlib_metadata.py`)
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
import socket
import threading
import time
import re

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

import django
import django.conf
settings = django.conf.settings

os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

# Override paths when running frozen
if getattr(sys, 'frozen', False):
    INTERNAL_DIR = os.path.join(os.path.dirname(sys.executable), '_internal')
    settings.DATABASES['default']['NAME'] = os.path.join(INTERNAL_DIR, 'db.sqlite3')
    settings.TEMPLATES[0]['DIRS'] = [os.path.join(INTERNAL_DIR, 'templates')]
    settings.STATICFILES_DIRS = [os.path.join(INTERNAL_DIR, 'static')]
    settings.STATIC_ROOT = os.path.join(INTERNAL_DIR, 'staticfiles')

# Backup fix: add _internal to sys.path for importlib.metadata
if getattr(sys, 'frozen', False):
    _internal_path = os.path.join(os.path.dirname(sys.executable), '_internal')
    sys.path.insert(0, _internal_path)

django.setup()

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
                message = '\u062a\u0645 \u062d\u0641\u0638 \u0627\u0644\u0645\u0644\u0641 \u0641\u064a \u0645\u062c\u0644\u062f \u0627\u0644\u062a\u0646\u0632\u064a\u0644\u0627\u062a: ' + filename
            except Exception as e:
                message = '\u062e\u0637\u0623 \u0641\u064a \u062d\u0641\u0638 \u0627\u0644\u0645\u0644\u0641: ' + str(e)

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

for i in range(20):
    try:
        s = socket.create_connection((HOST, PORT), timeout=0.5)
        s.close()
        break
    except:
        time.sleep(0.5)

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
1. ~~PDF Export - `FPDFUnicodeEncodingException`~~ **(تم الإصلاح)** تم تعديل `apps/occasions/views.py` لاستخدام خط عربي ديناميكي من Windows (`arabtype.ttf` أو `trado.ttf`) مع `set_text_shaping`
2. ~~Startup crash - `importlib.metadata.PackageNotFoundError: django-auditlog`~~ **(تم الإصلاح)** تم إنشاء `rthook_importlib_metadata.py` (runtime hook يُحقن قبل أي كود) يضبط `importlib.metadata.version()` ليبحث يدوياً في `_internal/*.dist-info` عند فشل البحث العادي في التطبيق المُجمّد
3. **Excel Export** - يعمل بشكل صحيح عبر DownloadMiddleware
4. **Database** - `db.sqlite3` مضمنة في `_internal/` ويجب تحديثها قبل البناء إذا تغيرت بيانات المستخدمين

## How to Rebuild EXE
1. فتح PowerShell في `D:\projects\ekhlas`
2. تشغيل أمر PyInstaller أعلاه
3. الانتظار ~4 دقائق
4. التشغيل من `D:\projects\ekhlas\dist\AlmajidApp\AlmajidApp.exe`

## How to Run Without Building (Dev)
```powershell
cd D:\projects\ekhlas
python desktop_app.py
```

## Recent Changes (Session: تغيير الملكية لمؤسسة الماجد)
- تم تغيير اسم التطبيق من "EkhlasApp" إلى "AlmajidApp"
- تم تغيير اسم المؤسسة من "جمعية الإخلاص الخيرية" إلى "مؤسسة الماجد"
- تم تغيير اسم النظام من "نظام الإدارة المتكامل" إلى "الجهاز الاداري"
- تم استبدال الشعار و icon.ico بالشعار الجديد (من media/logo1.jpg)
- تم إصلاح مشكلة تصدير PDF بالعربية في occasions/views.py
- تم تغيير البريد الإداري من admin@ekhlas.org.sa إلى admin@almajid.sa
- تم تحديث issuer الـ OTP من "الإخلاص" إلى "الماجد"
- تم تحديث ملف البروشور create_brochure.py بالاسم الجديد

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

1. **PDF Export** - `FPDFUnicodeEncodingException` في `apps/occasions/views.py`
   - السبب: fpdf2 يحاول كتابة نصوص عربية بالترميز latin-1
   - الحل المتوقع: إضافة خط يدعم UTF-8 مثل `DejaVu Sans` (ملف `.ttf`) إلى المشروع واستخدامه مع `add_font()`
   - لم يتم إصلاحها بعد، المستخدم قد يطلب ذلك لاحقاً

2. **قاعدة البيانات** - `db.sqlite3` يجب تحديثها قبل البناء
3. **لو أضيفت أي features جديدة**، يجب إعادة بناء الـ EXE

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
