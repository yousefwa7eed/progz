import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.validators import egypt_phone, egypt_national_id, EGYPT_GOVERNORATES


class DonorCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_("اسم التصنيف"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))
    priority = models.IntegerField(default=0, verbose_name=_("أولوية التواصل"))

    class Meta:
        ordering = ['-priority']
        verbose_name = _("تصنيف متبرع")
        verbose_name_plural = _("تصنيفات المتبرعين")

    def __str__(self):
        return self.name


class Donor(models.Model):
    DONOR_TYPES = [
        ('individual', 'فرد'),
        ('company', 'شركة'),
        ('organization', 'مؤسسة'),
    ]
    PREFERRED_CONTACT = [
        ('phone', 'اتصال هاتفي'),
        ('whatsapp', 'واتساب'),
        ('email', 'بريد إلكتروني'),
        ('sms', 'رسالة نصية'),
    ]
    PREFERRED_DONATION = [
        ('cash', 'نقدي'),
        ('in_kind', 'عيني'),
        ('sponsorship', 'كفالة'),
        ('project', 'مشروع'),
        ('zakat', 'زكاة'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("كود المتبرع"))
    full_name = models.CharField(max_length=255, verbose_name=_("الاسم"))
    donor_type = models.CharField(max_length=20, choices=DONOR_TYPES, default='individual', verbose_name=_("النوع"))
    phone = models.CharField(max_length=20, validators=[egypt_phone], verbose_name=_("رقم الموبايل"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("البريد"))
    address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))
    city = models.CharField(max_length=100, blank=True, null=True, choices=EGYPT_GOVERNORATES, verbose_name=_("المحافظة"))
    national_id = models.CharField(max_length=20, blank=True, null=True, validators=[egypt_national_id], verbose_name=_("الرقم القومي"))
    commercial_reg = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("السجل التجاري"))
    contact_person = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("شخص التواصل"))
    preferred_contact = models.CharField(max_length=20, choices=PREFERRED_CONTACT, default='phone', verbose_name=_("طريقة التواصل"))
    preferred_donation = models.CharField(max_length=20, choices=PREFERRED_DONATION, blank=True, null=True, verbose_name=_("نوع التبرع المفضل"))
    is_anonymous = models.BooleanField(default=False, verbose_name=_("متبرع مجهول"))
    is_committed = models.BooleanField(default=False, verbose_name=_("متبرع منتظم"))
    total_donations = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("إجمالي التبرعات"))
    last_donation_date = models.DateField(null=True, blank=True, verbose_name=_("آخر تبرع"))
    donor_category = models.ForeignKey(DonorCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='donors', verbose_name=_("التصنيف"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ التسجيل"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_donors', verbose_name=_("مسجل بواسطة"))
    history = HistoricalRecords()

    class Meta:
        ordering = ['-total_donations']
        verbose_name = _("متبرع")
        verbose_name_plural = _("المتبرعين")
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['full_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return f"{self.code} - {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = Donor.objects.order_by('created_at').last()
            num = 1 if not last else int(last.code.split('-')[-1]) + 1
            self.code = f"DNR-{num:05d}"
        super().save(*args, **kwargs)
