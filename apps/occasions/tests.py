from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Occasion

User = get_user_model()


class OccasionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='occasionuser', password='TestPass123!')

    def setUp(self):
        self.client.login(username='occasionuser', password='TestPass123!')

    def test_occasion_list_view(self):
        response = self.client.get(reverse('occasion_list'))
        self.assertEqual(response.status_code, 200)

    def test_occasion_create(self):
        response = self.client.post(reverse('occasion_add'), {
            'name': 'مناسبة تجريبية',
            'support_type': 'food',
            'start_date': '2026-01-01',
            'status': 'active',
        })
        self.assertEqual(Occasion.objects.count(), 1)
        self.assertEqual(Occasion.objects.first().name, 'مناسبة تجريبية')

    def test_occasion_detail(self):
        occasion = Occasion.objects.create(name='مناسبة للتفاصيل', support_type='food')
        response = self.client.get(reverse('occasion_detail', args=[occasion.pk]))
        self.assertEqual(response.status_code, 200)

    def test_occasion_delete(self):
        occasion = Occasion.objects.create(name='مناسبة للحذف', support_type='food')
        response = self.client.post(reverse('occasion_delete', args=[occasion.pk]))
        self.assertRedirects(response, reverse('occasion_list'))
        self.assertFalse(Occasion.objects.filter(pk=occasion.pk).exists())

    def test_occasion_export_excel(self):
        occasion = Occasion.objects.create(name='مناسبة للتصدير', support_type='food')
        response = self.client.get(reverse('occasion_export_excel', args=[occasion.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.openxmlformats', response['Content-Type'])
