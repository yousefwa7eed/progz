import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class Case(models.Model):
    CASE_TYPES = [
        ('financial', 'مساعدات مالية'),
        ('food', 'مساعدات غذائية'),
        ('cloth', 'كسوة'),
        ('medical', 'علاج'),
        ('educational', 'مساعدات تعليمية'),
        ('housing', 'ترميم/إسكان'),
        ('emergency', 'طارئة'),
        ('other', 'أخرى'),
    ]
    PRIORITY = [
        ('urgent', 'عاجلة'),
        ('high', 'عالية'),
        ('medium', 'متوسطة'),
        ('low', 'منخفضة'),
    ]
    STATUS = [
        ('new', 'جديد'),
        ('under_study', 'قيد الدراسة'),
        ('approved', 'معتمد'),
        ('disbursed', 'تم الصرف'),
        ('closed', 'مغلق'),
        ('rejected', 'مرفوض'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("رقم الحالة"))
    beneficiary = models.ForeignKey('beneficiaries.Beneficiary', on_delete=models.CASCADE, related_name='cases', verbose_name=_("المستفيد"))
    case_type = models.CharField(max_length=20, choices=CASE_TYPES, verbose_name=_("نوع المساعدة"))
    priority = models.CharField(max_length=20, choices=PRIORITY, default='medium', verbose_name=_("الأولوية"))
    description = models.TextField(verbose_name=_("وصف الحالة"))
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_("المبلغ المطلوب"))
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_("المبلغ المعتمد"))
    status = models.CharField(max_length=20, choices=STATUS, default='new', verbose_name=_("الحالة"))
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases', verbose_name=_("المسند إلى"))
    reviewed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_cases', verbose_name=_("المراجع"))
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_cases', verbose_name=_("المعتمد"))
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ المراجعة"))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الاعتماد"))
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الإغلاق"))
    close_reason = models.TextField(blank=True, null=True, verbose_name=_("سبب الإغلاق"))
    needs_reassessment = models.BooleanField(default=False, verbose_name=_("يحتاج إعادة تقييم"))
    reassessment_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ إعادة التقييم"))
    attachments = models.JSONField(default=list, blank=True, verbose_name=_("المرفقات"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_cases', verbose_name=_("منشأ بواسطة"))
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("حالة")
        verbose_name_plural = _("الحالات")
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['case_type']),
        ]

    def __str__(self):
        return f"{self.code} - {self.beneficiary.full_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = Case.objects.order_by('created_at').last()
            num = 1 if not last else int(last.code.split('-')[-1]) + 1
            self.code = f"CSE-{num:05d}"
        super().save(*args, **kwargs)


class CaseActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='activities', verbose_name=_("الحالة"))
    activity_type = models.CharField(max_length=50, verbose_name=_("نوع النشاط"))
    description = models.TextField(verbose_name=_("الوصف"))
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("منفذ النشاط"))
    old_status = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("الحالة القديمة"))
    new_status = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("الحالة الجديدة"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ النشاط"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("نشاط حالة")
        verbose_name_plural = _("نشاطات الحالات")

    def __str__(self):
        return f"{self.case.code} - {self.activity_type}"


class CaseImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='images', verbose_name=_("الحالة"))
    image = models.ImageField(upload_to='cases/', verbose_name=_("الصورة"))
    label = models.CharField(max_length=100, verbose_name=_("تسمية الصورة"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الرفع"))

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _("صورة حالة")
        verbose_name_plural = _("صور الحالات")

    def __str__(self):
        return f"{self.case.code} - {self.label}"


class CaseFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='features', verbose_name=_("الحالة"))
    name = models.CharField(max_length=100, verbose_name=_("الخاصية"))
    value = models.TextField(verbose_name=_("القيمة"))

    class Meta:
        ordering = ['name']
        verbose_name = _("خاصية حالة")
        verbose_name_plural = _("خصائص الحالات")

    def __str__(self):
        return f"{self.case.code} - {self.name}: {self.value}"
