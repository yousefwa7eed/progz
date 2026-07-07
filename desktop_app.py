import os
import sys
import json
import socket
import threading
import time
import re

# ── Load Supabase/DB config from external JSON file ──────────
# This must run BEFORE Django imports so settings.py picks up the env vars.
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
    # Only override SQLite path when NOT using Supabase
    if not _using_supabase:
        DATA_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'AlmajidApp', 'data')
        os.makedirs(DATA_DIR, exist_ok=True)
        DB_PATH = os.path.join(DATA_DIR, 'db.sqlite3')
        # Copy bundled database on first run
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

# Force PyInstaller to bundle psycopg2 for PostgreSQL (Supabase) support
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
