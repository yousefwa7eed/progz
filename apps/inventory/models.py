import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class InventoryCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_("اسم التصنيف"))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name=_("التصنيف الأب"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))

    class Meta:
        ordering = ['name']
        verbose_name = _("تصنيف مخزني")
        verbose_name_plural = _("تصنيفات المخزون")

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("كود الصنف"))
    name = models.CharField(max_length=255, verbose_name=_("اسم الصنف"))
    category = models.ForeignKey(InventoryCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='items', verbose_name=_("التصنيف"))
    unit = models.CharField(max_length=50, verbose_name=_("وحدة القياس"))
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("الكمية الحالية"))
    min_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("الحد الأدنى"))
    max_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name=_("الحد الأقصى"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("سعر الوحدة"))
    expiry_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ انتهاء الصلاحية"))
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("موقع التخزين"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['name']
        verbose_name = _("صنف مخزني")
        verbose_name_plural = _("الأصناف المخزنية")
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = InventoryItem.objects.order_by('created_at').last()
            num = 1 if not last else int(last.code.split('-')[-1]) + 1
            self.code = f"ITM-{num:05d}"
        super().save(*args, **kwargs)


class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('receive', 'استلام'),
        ('disburse', 'صرف'),
        ('return', 'مرتجع'),
        ('inventory', 'جرد'),
        ('transfer', 'تحويل'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions', verbose_name=_("الصنف"))
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name=_("نوع الحركة"))
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("الكمية"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("سعر الوحدة"))
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("الإجمالي"))
    source = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("المصدر"))
    donation = models.ForeignKey('donations.Donation', on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions', verbose_name=_("تبرع عيني"))
    beneficiary = models.ForeignKey('beneficiaries.Beneficiary', on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions', verbose_name=_("مستفيد"))
    case = models.ForeignKey('cases.Case', on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions', verbose_name=_("حالة"))
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions', verbose_name=_("مشروع"))
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("منفذ الحركة"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الحركة"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("حركة مخزنية")
        verbose_name_plural = _("الحركات المخزنية")

    def __str__(self):
        return f"{self.item.name} - {self.get_transaction_type_display()} - {self.quantity}"

    def save(self, *args, **kwargs):
        is_new = not self.pk
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        if is_new:
            item = self.item
            if self.transaction_type == 'receive':
                item.quantity += self.quantity
            elif self.transaction_type == 'disburse':
                item.quantity -= self.quantity
            elif self.transaction_type == 'return':
                item.quantity += self.quantity
            elif self.transaction_type == 'inventory':
                item.quantity = self.quantity
            item.save(update_fields=['quantity'])
