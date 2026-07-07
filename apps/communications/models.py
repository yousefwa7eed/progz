import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Communication(models.Model):
    TYPES = [
        ('email', 'بريد إلكتروني'),
        ('sms', 'رسالة نصية'),
        ('whatsapp', 'واتساب'),
        ('call', 'مكالمة'),
    ]
    DIRECTIONS = [
        ('incoming', 'وارد'),
        ('outgoing', 'صادر'),
    ]
    STATUS = [
        ('sent', 'مرسلة'),
        ('delivered', 'تم الاستلام'),
        ('read', 'مقروءة'),
        ('failed', 'فشلت'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    communication_type = models.CharField(max_length=20, choices=TYPES, verbose_name=_("النوع"))
    direction = models.CharField(max_length=20, choices=DIRECTIONS, default='outgoing', verbose_name=_("الاتجاه"))
    subject = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("الموضوع"))
    content = models.TextField(verbose_name=_("المحتوى"))
    sender = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_communications', verbose_name=_("المرسل"))
    recipient = models.CharField(max_length=255, verbose_name=_("المستلم"))
    donor = models.ForeignKey('donors.Donor', on_delete=models.SET_NULL, null=True, blank=True, related_name='communications', verbose_name=_("متبرع"))
    beneficiary = models.ForeignKey('beneficiaries.Beneficiary', on_delete=models.SET_NULL, null=True, blank=True, related_name='communications', verbose_name=_("مستفيد"))
    related_model = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("العنصر المرتبط"))
    related_id = models.UUIDField(null=True, blank=True, verbose_name=_("معرف العنصر"))
    status = models.CharField(max_length=20, choices=STATUS, default='sent', verbose_name=_("الحالة"))
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإرسال"))
    attachments = models.JSONField(default=list, blank=True, verbose_name=_("المرفقات"))

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("مراسلة")
        verbose_name_plural = _("المراسلات")

    def __str__(self):
        return f"{self.get_communication_type_display()} - {self.subject or 'بدون موضوع'}"
