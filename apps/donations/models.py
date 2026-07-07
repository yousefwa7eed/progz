import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.branches.models import Branch
from apps.projects.models import Project


class Donation(models.Model):
    DONATION_TYPES = [
        ('cash', 'نقدي'),
        ('in_kind', 'عيني'),
        ('electronic', 'إلكتروني'),
    ]
    PAYMENT_METHODS = [
        ('cash', 'نقداً'),
        ('transfer', 'تحويل بنكي'),
        ('card', 'بطاقة ائتمان'),
        ('wallet', 'محفظة إلكترونية'),
        ('cheque', 'شيك'),
    ]
    TRANSACTION_TYPES = [
        ('general', 'عام'),
        ('zakat', 'زكاة'),
        ('sadaqah', 'صدقة'),
        ('sponsorship', 'كفالة'),
        ('project', 'مشروع'),
        ('endowment', 'وقف'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("رقم التبرع"))
    donor = models.ForeignKey('donors.Donor', on_delete=models.SET_NULL, null=True, blank=True, related_name='donations', verbose_name=_("المتبرع"))
    donor_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("اسم المتبرع (للمجهول)"))
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES, verbose_name=_("نوع التبرع"))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash', verbose_name=_("طريقة الدفع"))
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("المبلغ"))
    currency = models.CharField(max_length=3, default='SAR', verbose_name=_("العملة"))
    items = models.JSONField(default=list, blank=True, verbose_name=_("الأصناف (للعيني)"))
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='general', verbose_name=_("نوع المعاملة"))
    campaign = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("الحملة"))
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations', verbose_name=_("المشروع"))
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations', verbose_name=_("الفرع"))
    received_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='received_donations', verbose_name=_("المستلم"))
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name=_("رقم الإيصال"))
    receipt_date = models.DateField(auto_now_add=True, verbose_name=_("تاريخ الإيصال"))
    is_anonymous = models.BooleanField(default=False, verbose_name=_("تبرع مجهول"))
    is_zakat = models.BooleanField(default=False, verbose_name=_("زكاة"))
    zakat_year = models.IntegerField(blank=True, null=True, verbose_name=_("سنة الزكاة"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    attachments = models.JSONField(default=list, blank=True, verbose_name=_("المرفقات"))
    status = models.CharField(max_length=20, choices=[
        ('recorded', 'مسجل'),
        ('confirmed', 'مؤكد'),
        ('cancelled', 'ملغي'),
    ], default='recorded', verbose_name=_("الحالة"))
    is_deposited = models.BooleanField(default=False, verbose_name=_("تم الإيداع"))
    deposited_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ الإيداع"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ التسجيل"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_donations', verbose_name=_("مسجل بواسطة"))
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("تبرع")
        verbose_name_plural = _("التبرعات")
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['receipt_number']),
            models.Index(fields=['donation_type']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['receipt_date']),
        ]

    def __str__(self):
        return f"{self.code} - {self.amount} SAR"

    def save(self, *args, **kwargs):
        if not self.code:
            last = Donation.objects.order_by('created_at').last()
            num = 1 if not last else int(last.code.split('-')[-1]) + 1
            self.code = f"DON-{num:05d}"
        if not self.receipt_number:
            last = Donation.objects.order_by('created_at').last()
            num = 1 if not last else int(last.receipt_number.split('-')[-1]) + 1
            self.receipt_number = f"REC-{num:05d}"
        super().save(*args, **kwargs)
        if self.donor and self.status == 'confirmed':
            donor = self.donor
            donor.total_donations = Donation.objects.filter(donor=donor, status='confirmed').aggregate(
                total=models.Sum('amount'))['total'] or 0
            donor.last_donation_date = Donation.objects.filter(donor=donor, status='confirmed').order_by(
                '-receipt_date').first().receipt_date if Donation.objects.filter(donor=donor,
                status='confirmed').exists() else None
            donor.save(update_fields=['total_donations', 'last_donation_date'])


class DonationItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='donation_items', verbose_name=_("التبرع"))
    name = models.CharField(max_length=255, verbose_name=_("اسم الصنف"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("الكمية"))
    unit = models.CharField(max_length=50, verbose_name=_("الوحدة"))
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("القيمة التقديرية"))

    class Meta:
        verbose_name = _("صنف تبرع")
        verbose_name_plural = _("أصناف التبرعات")

    def __str__(self):
        return f"{self.name} x{self.quantity}"
