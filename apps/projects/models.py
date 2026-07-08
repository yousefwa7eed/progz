import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class Project(models.Model):
    PROJECT_TYPES = [
        ('food', 'توزيع غذاء'),
        ('clothing', 'كسوة الشتاء'),
        ('water', 'سقيا المياه'),
        ('medical', 'دعم العلاج'),
        ('renovation', 'ترميم المنازل'),
        ('educational', 'مساعدات تعليمية'),
        ('seasonal', 'مساعدات موسمية'),
        ('iftar', 'إفطار صائم'),
        ('other', 'أخرى'),
    ]
    STATUS = [
        ('planning', 'تخطيط'),
        ('approved', 'معتمد'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'منتهي'),
        ('cancelled', 'ملغي'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("رقم المشروع"))
    name = models.CharField(max_length=255, verbose_name=_("اسم المشروع"))
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES, verbose_name=_("نوع المشروع"))
    description = models.TextField(verbose_name=_("وصف المشروع"))
    goal_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("الهدف المالي"))
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("إجمالي الميزانية"))
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("إجمالي المنصرف"))
    start_date = models.DateField(verbose_name=_("تاريخ البداية"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ النهاية"))
    status = models.CharField(max_length=20, choices=STATUS, default='planning', verbose_name=_("الحالة"))
    manager = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects', verbose_name=_("مدير المشروع"))
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_projects', verbose_name=_("المعتمد"))
    beneficiaries_count = models.IntegerField(default=0, verbose_name=_("عدد المستفيدين"))
    locations = models.TextField(blank=True, null=True, verbose_name=_("مواقع التنفيذ"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    attachments = models.JSONField(default=list, blank=True, verbose_name=_("المرفقات"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects', verbose_name=_("منشأ بواسطة"))
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("مشروع")
        verbose_name_plural = _("المشاريع")
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['project_type']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = Project.objects.order_by('created_at').last()
            num = 1 if not last else int(last.code.split('-')[-1]) + 1
            self.code = f"PRJ-{num:05d}"
        super().save(*args, **kwargs)


class ProjectPhase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='phases', verbose_name=_("المشروع"))
    name = models.CharField(max_length=255, verbose_name=_("اسم المرحلة"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))
    start_date = models.DateField(verbose_name=_("تاريخ البداية"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ النهاية"))
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("الميزانية"))
    spent = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("المنصرف"))
    status = models.CharField(max_length=20, choices=[
        ('pending', 'قادمة'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'منجزة'),
    ], default='pending', verbose_name=_("الحالة"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))

    class Meta:
        ordering = ['start_date']
        verbose_name = _("مرحلة مشروع")
        verbose_name_plural = _("مراحل المشروع")
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.name}"
