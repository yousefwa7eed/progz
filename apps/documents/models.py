import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('id', 'هوية'),
        ('report', 'تقرير'),
        ('contract', 'عقد'),
        ('receipt', 'إيصال'),
        ('photo', 'صورة'),
        ('medical', 'تقرير طبي'),
        ('study', 'دراسة حالة'),
        ('other', 'أخرى'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("رقم الوثيقة"))
    title = models.CharField(max_length=255, verbose_name=_("العنوان"))
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name=_("النوع"))
    file = models.FileField(upload_to='documents/%Y/%m/', verbose_name=_("الملف"))
    file_size = models.IntegerField(default=0, verbose_name=_("حجم الملف"))
    file_type = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("نوع الملف"))
    related_model = models.CharField(max_length=50, verbose_name=_("النموذج المرتبط"))
    related_id = models.UUIDField(verbose_name=_("معرف العنصر"))
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("الرافع"))
    is_confidential = models.BooleanField(default=False, verbose_name=_("سري"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الرفع"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("وثيقة")
        verbose_name_plural = _("الوثائق")
        indexes = [
            models.Index(fields=['related_model', 'related_id']),
        ]

    def __str__(self):
        return f"{self.code} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = Document.objects.order_by('created_at').last()
            num = 1 if not last else int(last.code.split('-')[-1]) + 1
            self.code = f"DOC-{num:05d}"
        super().save(*args, **kwargs)
