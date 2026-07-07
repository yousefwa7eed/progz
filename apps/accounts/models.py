import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from apps.validators import egypt_phone


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_("اسم الدور"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("كود الدور"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))
    priority = models.IntegerField(default=0, verbose_name=_("الأولوية"))
    is_system = models.BooleanField(default=False, verbose_name=_("دور نظامي"))

    class Meta:
        ordering = ['priority']
        verbose_name = _("دور")
        verbose_name_plural = _("الأدوار")

    def __str__(self):
        return self.name


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_("اسم الصلاحية"))
    codename = models.CharField(max_length=100, unique=True, verbose_name=_("كود الصلاحية"))
    module = models.CharField(max_length=50, verbose_name=_("الوحدة"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))
    roles = models.ManyToManyField(Role, related_name='permissions', blank=True, verbose_name=_("الأدوار"))

    class Meta:
        ordering = ['module', 'name']
        verbose_name = _("صلاحية")
        verbose_name_plural = _("الصلاحيات")

    def __str__(self):
        return f"[{self.module}] {self.name}"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255, verbose_name=_("الاسم الكامل"))
    phone = models.CharField(max_length=20, blank=True, null=True, validators=[egypt_phone], verbose_name=_("رقم الموبايل"))
    national_id = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("رقم الهوية"))
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users', verbose_name=_("الدور"))
    extra_permissions = models.ManyToManyField(Permission, blank=True, related_name='extra_users', verbose_name=_("صلاحيات إضافية"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("محذوف"))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الحذف"))
    otp_secret = models.CharField(max_length=32, blank=True, null=True, verbose_name=_("سر 2FA"))
    otp_enabled = models.BooleanField(default=False, verbose_name=_("تفعيل 2FA"))
    session_token = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users', verbose_name=_("منشأ بواسطة"))

    class Meta:
        ordering = ['-date_joined']
        verbose_name = _("مستخدم")
        verbose_name_plural = _("المستخدمين")

    def __str__(self):
        return self.full_name or self.username

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.username
        super().save(*args, **kwargs)
