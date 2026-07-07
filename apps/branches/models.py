import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("كود الفرع"))
    name = models.CharField(max_length=255, verbose_name=_("اسم الفرع"))
    address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("المدينة"))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("الهاتف"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("البريد الإلكتروني"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    class Meta:
        ordering = ['name']
        verbose_name = _("فرع")
        verbose_name_plural = _("الفروع")

    def __str__(self):
        return self.name
