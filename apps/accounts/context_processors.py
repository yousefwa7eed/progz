from django.conf import settings

def site_settings(request):
    return {
        'site_name': 'مؤسسة الماجد - الجهاز الاداري',
        'site_short_name': 'الماجد',
        'debug': settings.DEBUG,
        'currency': getattr(settings, 'LOCAL_CURRENCY', 'EGP'),
    }
