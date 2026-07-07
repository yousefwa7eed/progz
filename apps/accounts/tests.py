from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTests(TestCase):
    def test_register_view_creates_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_rejects_weak_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'weakuser',
            'password': '1234',
            'password_confirm': '1234',
        })
        self.assertContains(response, '8 أحرف على الأقل')
        self.assertFalse(User.objects.filter(username='weakuser').exists())

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(reverse('register'), {
            'username': 'mismatchuser',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass1!',
        })
        self.assertContains(response, 'غير متطابق')

    def test_login_view_succeeds(self):
        User.objects.create_user(username='logintest', password='TestPass123!')
        response = self.client.post(reverse('login'), {
            'username': 'logintest',
            'password': 'TestPass123!',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_view_fails_wrong_password(self):
        User.objects.create_user(username='loginfail', password='TestPass123!')
        response = self.client.post(reverse('login'), {
            'username': 'loginfail',
            'password': 'wrongpassword',
        })
        self.assertContains(response, 'بيانات الدخول غير صحيحة')

    def test_logout_redirects_to_login(self):
        User.objects.create_user(username='logouttest', password='TestPass123!')
        self.client.login(username='logouttest', password='TestPass123!')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_authenticated_user_can_access_dashboard(self):
        User.objects.create_user(username='dashuser', password='TestPass123!')
        self.client.login(username='dashuser', password='TestPass123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
