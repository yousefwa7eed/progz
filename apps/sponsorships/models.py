import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class Sponsorship(models.Model):
    SPONSORSHIP_TYPES = [
        ('orphan', 'كفالة يتيم'),
        ('family', 'كفالة أسرة'),
        ('patient', 'كفالة مريض'),
        ('student', 'كفالة طالب علم'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("رقم الكفالة"))
    sponsor = models.ForeignKey('donors.Donor', on_delete=models.CASCADE, related_name='sponsorships', verbose_name=_("الكفيل"))
    beneficiary = models.ForeignKey('beneficiaries.Beneficiary', on_delete=models.CASCADE, related_name='sponsorships', verbose_name=_("المستفيد"))
    sponsorship_type = models.CharField(max_length=20, choices=SPONSORSHIP_TYPES, verbose_name=_("نوع الكفالة"))
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("المبلغ الشهري"))
    start_date = models.DateField(verbose_name=_("تاريخ البدء"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ الانتهاء"))
    duration_months = models.IntegerField(default=12, verbose_name=_("المدة (شهر)"))
    is_permanent = models.BooleanField(default=False, verbose_name=_("مستمرة"))
    payment_method = models.CharField(max_length=20, choices=[
        ('cash', 'نقداً'),
        ('transfer', 'تحويل بنكي'),
        ('automatic', 'خصم آلي'),
        ('card', 'بطاقة'),
    ], default='transfer', verbose_name=_("طريقة الدفع"))
    payment_day = models.IntegerField(default=1, verbose_name=_("يوم الدفع"))
    is_active = models.BooleanField(default=True, verbose_name=_("سارية"))
    status = models.CharField(max_length=20, choices=[
        ('active', 'نشطة'),
        ('paused', 'متوقفة'),
        ('expired', 'منتهية'),
        ('cancelled', 'ملغاة'),
    ], default='active', verbose_name=_("الحالة"))
    last_payment_date = models.DateField(null=True, blank=True, verbose_name=_("آخر صرف"))
    next_payment_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ الصرف القادم"))
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("إجمالي المدفوع"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("منشأ بواسطة"))
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("كفالة")
        verbose_name_plural = _("الكفالات")
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['sponsorship_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.code} - {self.get_sponsorship_type_display()}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = Sponsorship.objects.order_by('created_at').last()
            num = 1 if not last else int(last.code.split('-')[-1]) + 1
            self.code = f"SPN-{num:05d}"
        super().save(*args, **kwargs)


class SponsorshipPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sponsorship = models.ForeignKey(Sponsorship, on_delete=models.CASCADE, related_name='payments', verbose_name=_("الكفالة"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("المبلغ"))
    payment_date = models.DateField(verbose_name=_("تاريخ الدفع"))
    month = models.IntegerField(verbose_name=_("الشهر"))
    year = models.IntegerField(verbose_name=_("السنة"))
    is_donor_paid = models.BooleanField(default=True, verbose_name=_("تم الدفع من الكفيل"))
    is_beneficiary_received = models.BooleanField(default=False, verbose_name=_("استلم المستفيد"))
    receipt_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("رقم الإيصال"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("مسجل بواسطة"))

    class Meta:
        ordering = ['-payment_date']
        verbose_name = _("دفعة كفالة")
        verbose_name_plural = _("دفعات الكفالات")
        unique_together = ['sponsorship', 'month', 'year']

    def __str__(self):
        return f"{self.sponsorship.code} - {self.month}/{self.year}"

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new:
            sponsorship = self.sponsorship
            sponsorship.total_paid = SponsorshipPayment.objects.filter(
                sponsorship=sponsorship).aggregate(total=models.Sum('amount'))['total'] or 0
            sponsorship.last_payment_date = payment_date = SponsorshipPayment.objects.filter(
                sponsorship=sponsorship).order_by('-payment_date').first()
            sponsorship.save(update_fields=['total_paid', 'last_payment_date'])
