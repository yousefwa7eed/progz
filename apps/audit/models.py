import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    ACTIONS = [
        ('create', 'إنشاء'),
        ('update', 'تعديل'),
        ('delete', 'حذف'),
        ('view', 'قراءة'),
        ('login', 'تسجيل دخول'),
        ('logout', 'تسجيل خروج'),
        ('approve', 'اعتماد'),
        ('reject', 'رفض'),
        ('disburse', 'صرف'),
        ('export', 'تصدير'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=20, choices=ACTIONS, verbose_name=_("الإجراء"))
    actor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs', verbose_name=_("المستخدم"))
    model_name = models.CharField(max_length=100, verbose_name=_("اسم النموذج"))
    model_id = models.UUIDField(verbose_name=_("معرف العنصر"), db_index=True)
    changes = models.JSONField(default=dict, blank=True, verbose_name=_("التغييرات"))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP"))
    user_agent = models.TextField(blank=True, null=True, verbose_name=_("المتصفح"))
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("الفرع"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("الوقت"), db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("سجل تدقيق")
        verbose_name_plural = _("سجلات التدقيق")
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['model_name', 'model_id']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name} - {self.timestamp}"


class Notification(models.Model):
    TYPES = [
        ('info', 'معلومات'),
        ('success', 'نجاح'),
        ('warning', 'تنبيه'),
        ('error', 'خطأ'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications', verbose_name=_("المستخدم"))
    title = models.CharField(max_length=255, verbose_name=_("العنوان"))
    message = models.TextField(verbose_name=_("الرسالة"))
    notification_type = models.CharField(max_length=20, choices=TYPES, default='info', verbose_name=_("النوع"))
    is_read = models.BooleanField(default=False, verbose_name=_("مقروء"))
    related_model = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("النموذج المرتبط"))
    related_id = models.UUIDField(null=True, blank=True, verbose_name=_("معرف العنصر"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("إشعار")
        verbose_name_plural = _("الإشعارات")
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return self.title


class BackupLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255, verbose_name=_("اسم الملف"))
    file_size = models.BigIntegerField(default=0, verbose_name=_("حجم الملف"))
    status = models.CharField(max_length=20, choices=[('success', 'نجاح'), ('failed', 'فشل')], verbose_name=_("الحالة"))
    backup_type = models.CharField(max_length=20, choices=[('auto', 'تلقائي'), ('manual', 'يدوي')], default='auto', verbose_name=_("النوع"))
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("مسار الحفظ"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("سجل نسخ احتياطي")
        verbose_name_plural = _("سجلات النسخ الاحتياطي")

    def __str__(self):
        return f"{self.file_name} - {self.get_status_display()}"


class SystemSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True, verbose_name=_("المفتاح"))
    value = models.JSONField(verbose_name=_("القيمة"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))
    is_encrypted = models.BooleanField(default=False, verbose_name=_("مشفر"))
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("آخر تعديل"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("إعداد النظام")
        verbose_name_plural = _("إعدادات النظام")

    def __str__(self):
        return self.key
