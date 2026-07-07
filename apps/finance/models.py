import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class Account(models.Model):
    ACCOUNT_GROUPS = [
        ('asset', 'أصول'),
        ('liability', 'خصوم'),
        ('income', 'إيرادات'),
        ('expense', 'مصروفات'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("كود الحساب"))
    name = models.CharField(max_length=255, verbose_name=_("اسم الحساب"))
    account_type = models.CharField(max_length=20, choices=[('main', 'رئيسي'), ('sub', 'فرعي')], verbose_name=_("النوع"))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name=_("الحساب الأب"))
    account_group = models.CharField(max_length=20, choices=ACCOUNT_GROUPS, verbose_name=_("المجموعة"))
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("الرصيد الافتتاحي"))
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("الرصيد الحالي"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']
        verbose_name = _("حساب")
        verbose_name_plural = _("دليل الحسابات")

    def __str__(self):
        return f"{self.code} - {self.name}"


class ExpenseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_("الاسم"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("الكود"))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name=_("التصنيف الأب"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    class Meta:
        ordering = ['code']
        verbose_name = _("تصنيف مصروف")
        verbose_name_plural = _("تصنيفات المصروفات")

    def __str__(self):
        return f"{self.code} - {self.name}"


class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('current', 'جاري'),
        ('savings', 'استثماري'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=255, verbose_name=_("اسم البنك"))
    account_name = models.CharField(max_length=255, verbose_name=_("اسم الحساب"))
    account_number = models.CharField(max_length=50, verbose_name=_("رقم الحساب"))
    iban = models.CharField(max_length=34, verbose_name=_("IBAN"))
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='current', verbose_name=_("النوع"))
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("الرصيد الحالي"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    class Meta:
        verbose_name = _("حساب بنكي")
        verbose_name_plural = _("الحسابات البنكية")

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class FinancialEntry(models.Model):
    ENTRY_TYPES = [
        ('income', 'إيراد'),
        ('expense', 'مصروف'),
        ('transfer', 'تحويل'),
    ]
    TRANSACTION_TYPES = [
        ('general', 'عام'),
        ('zakat', 'زكاة'),
        ('sadaqah', 'صدقة'),
        ('sponsorship', 'كفالة'),
        ('project', 'مشروع'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("رقم القيد"))
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, verbose_name=_("نوع القيد"))
    entry_date = models.DateField(verbose_name=_("تاريخ القيد"))
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("المبلغ"))
    currency = models.CharField(max_length=3, default='SAR', verbose_name=_("العملة"))
    description = models.TextField(verbose_name=_("البيان"))
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='entries', verbose_name=_("الحساب"))
    donor = models.ForeignKey('donors.Donor', on_delete=models.SET_NULL, null=True, blank=True, related_name='entries', verbose_name=_("متبرع"))
    donation = models.ForeignKey('donations.Donation', on_delete=models.SET_NULL, null=True, blank=True, related_name='entries', verbose_name=_("تبرع"))
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='entries', verbose_name=_("تصنيف المصروف"))
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='entries', verbose_name=_("مشروع"))
    case = models.ForeignKey('cases.Case', on_delete=models.SET_NULL, null=True, blank=True, related_name='entries', verbose_name=_("حالة"))
    payment_method = models.CharField(max_length=20, choices=[
        ('cash', 'نقداً'),
        ('transfer', 'تحويل بنكي'),
        ('card', 'بطاقة'),
        ('cheque', 'شيك'),
    ], default='cash', verbose_name=_("طريقة الدفع"))
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='entries', verbose_name=_("حساب بنكي"))
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("رقم مرجعي"))
    receipt_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("رقم الإيصال"))
    is_approved = models.BooleanField(default=False, verbose_name=_("معتمد"))
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_entries', verbose_name=_("المعتمد"))
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_entries', verbose_name=_("المسجل"))
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='general', verbose_name=_("نوع المعاملة الشرعية"))
    is_reconciled = models.BooleanField(default=False, verbose_name=_("تمت التسوية"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    attachments = models.JSONField(default=list, blank=True, verbose_name=_("المرفقات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ التسجيل"))
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-entry_date', '-created_at']
        verbose_name = _("قيد مالي")
        verbose_name_plural = _("القيود المالية")
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['entry_type']),
            models.Index(fields=['entry_date']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        return f"{self.code} - {self.amount} SAR"

    def save(self, *args, **kwargs):
        if not self.code:
            last = FinancialEntry.objects.order_by('created_at').last()
            num = 1 if not last else int(last.code.split('-')[-1]) + 1
            prefix = 'INC' if self.entry_type == 'income' else 'EXP' if self.entry_type == 'expense' else 'TRF'
            self.code = f"{prefix}-{num:05d}"
        super().save(*args, **kwargs)
