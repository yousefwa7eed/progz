import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.branches.models import Branch
from apps.validators import egypt_phone, egypt_national_id, EGYPT_GOVERNORATES


class Beneficiary(models.Model):
    MARITAL_STATUS = [
        ('single', 'أعزب/عزباء'),
        ('married', 'متزوج'),
        ('divorced', 'مطلق'),
        ('widowed', 'أرمل'),
    ]
    EMPLOYMENT_STATUS = [
        ('employed', 'موظف'),
        ('unemployed', 'عاطل'),
        ('retired', 'متقاعد'),
        ('student', 'طالب'),
        ('disabled', 'عاجز عن العمل'),
    ]
    HOUSING_TYPES = [
        ('owned', 'ملك'),
        ('rented', 'إيجار'),
        ('relative', 'مع أقارب'),
        ('other', 'أخرى'),
    ]
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('suspended', 'موقوف'),
        ('closed', 'مغلق'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("كود المستفيد"))
    full_name = models.CharField(max_length=255, verbose_name=_("الاسم الكامل"))
    gender = models.CharField(max_length=1, choices=[('M', 'ذكر'), ('F', 'أنثى')], verbose_name=_("الجنس"))
    national_id = models.CharField(max_length=20, blank=True, null=True, validators=[egypt_national_id], verbose_name=_("الرقم القومي"))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ الميلاد"))
    phone = models.CharField(max_length=20, validators=[egypt_phone], verbose_name=_("رقم الموبايل"))
    phone2 = models.CharField(max_length=20, blank=True, null=True, validators=[egypt_phone], verbose_name=_("موبايل آخر"))
    address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))
    city = models.CharField(max_length=100, blank=True, null=True, choices=EGYPT_GOVERNORATES, verbose_name=_("المحافظة"))
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("المنطقة"))
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS, blank=True, null=True, verbose_name=_("الحالة الاجتماعية"))
    family_members = models.IntegerField(default=1, verbose_name=_("عدد أفراد الأسرة"))
    has_orphans = models.BooleanField(default=False, verbose_name=_("يوجد أيتام"))
    orphans_count = models.IntegerField(default=0, verbose_name=_("عدد الأيتام"))
    health_status = models.TextField(blank=True, null=True, verbose_name=_("الحالة الصحية"))
    has_chronic_disease = models.BooleanField(default=False, verbose_name=_("أمراض مزمنة"))
    chronic_diseases = models.TextField(blank=True, null=True, verbose_name=_("تفاصيل الأمراض"))
    has_disabilities = models.BooleanField(default=False, verbose_name=_("إعاقات"))
    disabilities_details = models.TextField(blank=True, null=True, verbose_name=_("تفاصيل الإعاقات"))
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, blank=True, null=True, verbose_name=_("الوضع الوظيفي"))
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الدخل الشهري"))
    housing_type = models.CharField(max_length=20, choices=HOUSING_TYPES, blank=True, null=True, verbose_name=_("نوع السكن"))
    is_urgent = models.BooleanField(default=False, verbose_name=_("حالة عاجلة"))
    priority_score = models.IntegerField(default=0, verbose_name=_("درجة الأولوية"))
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='beneficiaries', verbose_name=_("الفرع"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_("الحالة"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    attachments = models.JSONField(default=list, blank=True, verbose_name=_("المرفقات"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ التسجيل"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_beneficiaries', verbose_name=_("مسجل بواسطة"))
    history = HistoricalRecords()

    class Meta:
        ordering = ['-priority_score', '-created_at']
        verbose_name = _("مستفيد")
        verbose_name_plural = _("المستفيدين")
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['full_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['city']),
            models.Index(fields=['status']),
            models.Index(fields=['is_urgent']),
        ]

    def __str__(self):
        return f"{self.code} - {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = Beneficiary.objects.order_by('created_at').last()
            num = 1 if not last else int(last.code.split('-')[-1]) + 1
            self.code = f"BEN-{num:05d}"
        self.priority_score = self._calculate_priority()
        super().save(*args, **kwargs)

    def _calculate_priority(self):
        score = 0
        if self.is_urgent:
            score += 50
        if self.has_orphans:
            score += 20
        if self.has_chronic_disease or self.has_disabilities:
            score += 15
        if self.monthly_income is not None and self.monthly_income < 1000:
            score += 10
        if self.marital_status in ['divorced', 'widowed']:
            score += 10
        if self.family_members is not None and self.family_members > 5:
            score += 5
        return min(score, 100)
