from django.conf import settings

def site_settings(request):
    return {
        'site_name': 'مؤسسة الماجد - الجهاز الاداري',
        'site_short_name': 'الماجد',
        'debug': settings.DEBUG,
        'currency': getattr(settings, 'LOCAL_CURRENCY', 'EGP'),
        'currency_symbol': getattr(settings, 'CURRENCY_SYMBOL', 'ج.م'),
        'currency_name': getattr(settings, 'CURRENCY_NAME', 'جنيه مصري'),
    }
