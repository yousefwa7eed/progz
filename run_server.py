import os, sys, re
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

import django, django.conf
settings = django.conf.settings
django.setup()

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

# Download middleware
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
                message = f'<p style="font-size:1.2em;color:#080">تم حفظ الملف في مجلد التحميلات:</p><p style="direction:ltr;background:#eee;padding:10px;border-radius:6px">{filename}</p>'
            except Exception as e:
                message = f'<p style="color:#c00">خطأ في حفظ الملف: {e}</p>'

            html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<title>تم التحميل</title><style>
body{{font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:#f5f5f5}}
.card{{background:#fff;padding:40px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.1);text-align:center;max-width:500px}}
.btn{{display:inline-block;margin:8px 4px;padding:10px 24px;background:#0d6efd;color:#fff;text-decoration:none;border-radius:6px;border:none;cursor:pointer}}
.btn-gray{{background:#6c757d}}
</style></head><body><div class="card"><h3>{message}</h3>
<button class="btn" onclick="window.history.back()">العودة</button>
<button class="btn btn-gray" onclick="window.close()">إغلاق</button>
<script>setTimeout(function(){{window.history.back()}}, 3000)</script>
</div></body></html>'''
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

import waitress
HOST = '0.0.0.0'
PORT = 8500
print(f'Server running at http://{HOST}:{PORT}')
print()
print('To create public URL, open another terminal and run:')
print(f'  ssh -R 80:localhost:{PORT} nokey@localhost.run')
print()
print('Press Ctrl+C to stop')
waitress.serve(app, host=HOST, port=PORT, threads=8, _quiet=False)
