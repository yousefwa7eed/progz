import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(username='testuser3').exists():
    u = User.objects.create_user(username='testuser3', password='testpass123', full_name='Test')

c = Client(enforce_csrf_checks=False)
c.login(username='testuser3', password='testpass123')

# GET form
response = c.get('/beneficiaries/add/')
print(f'GET status: {response.status_code}')
if response.status_code != 200:
    print(f'GET error: {response.content[:500]}')
else:
    # POST
    response = c.post('/beneficiaries/add/', {
        'full_name': 'Test User',
        'gender': 'M',
        'phone': '01234567890',
        'family_members': '1',
        'monthly_income': '0',
        'notes': '',
    }, follow=True)
    print(f'POST status: {response.status_code}')
    if response.status_code == 200:
        if len(response.redirect_chain) > 0:
            print(f'SUCCESS - Redirected to: {response.redirect_chain}')
        else:
            if 'error' in response.content.decode('utf-8').lower():
                print('Form has errors')
                import re
                errs = re.findall(r'alert[^>]*>(.*?)</div>', response.content.decode('utf-8'), re.DOTALL)
                for e in errs:
                    print(f'  - {e.strip()}')
            else:
                print(f'Rendered page (no redirect): {response.content[:200]}')
    else:
        print(f'Error: {response.status_code}')
