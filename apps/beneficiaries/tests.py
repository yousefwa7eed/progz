from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Beneficiary

User = get_user_model()


class BeneficiaryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='benefuser', password='TestPass123!')

    def setUp(self):
        self.client.login(username='benefuser', password='TestPass123!')

    def test_list_view(self):
        response = self.client.get(reverse('beneficiary_list'))
        self.assertEqual(response.status_code, 200)

    def test_create_beneficiary(self):
        response = self.client.post(reverse('beneficiary_add'), {
            'full_name': 'مستفيد تجريبي',
            'gender': 'M',
            'phone': '01234567890',
        })
        self.assertRedirects(response, reverse('beneficiary_list'))
        self.assertEqual(Beneficiary.objects.count(), 1)
        self.assertEqual(Beneficiary.objects.first().full_name, 'مستفيد تجريبي')

    def test_detail_view(self):
        b = Beneficiary.objects.create(full_name='مستفيد التفاصيل', gender='M', phone='01234567890', created_by=self.user)
        response = self.client.get(reverse('beneficiary_detail', args=[b.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'مستفيد التفاصيل')

    def test_update_beneficiary(self):
        b = Beneficiary.objects.create(full_name='قبل التعديل', gender='M', phone='01234567890', created_by=self.user)
        response = self.client.post(reverse('beneficiary_edit', args=[b.pk]), {
            'full_name': 'بعد التعديل',
            'gender': 'M',
            'phone': '01234567890',
        })
        self.assertRedirects(response, reverse('beneficiary_list'))
        b.refresh_from_db()
        self.assertEqual(b.full_name, 'بعد التعديل')

    def test_soft_delete_beneficiary(self):
        b = Beneficiary.objects.create(full_name='للحذف', gender='M', phone='01234567890', created_by=self.user)
        response = self.client.post(reverse('beneficiary_delete', args=[b.pk]))
        self.assertRedirects(response, reverse('beneficiary_list'))
        b.refresh_from_db()
        self.assertFalse(b.is_active)

    def test_export_excel_list(self):
        response = self.client.get(reverse('beneficiary_export_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.openxmlformats', response['Content-Type'])

    def test_export_detail_excel(self):
        b = Beneficiary.objects.create(full_name='تصدير اكسل', gender='M', phone='01234567890', created_by=self.user)
        response = self.client.get(reverse('beneficiary_export_detail_excel', args=[b.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.openxmlformats', response['Content-Type'])
