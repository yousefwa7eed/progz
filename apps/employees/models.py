import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.branches.models import Branch
from apps.validators import egypt_phone


class Employee(models.Model):
    EMPLOYEE_TYPES = [
        ('employee', 'موظف'),
        ('volunteer', 'متطوع'),
    ]
    CONTRACT_TYPES = [
        ('full_time', 'دوام كامل'),
        ('part_time', 'دوام جزئي'),
        ('volunteer', 'متطوع'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile', verbose_name=_("حساب النظام"))
    employee_code = models.CharField(max_length=20, unique=True, verbose_name=_("كود الموظف"))
    full_name = models.CharField(max_length=255, verbose_name=_("الاسم الكامل"))
    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPES, verbose_name=_("النوع"))
    position = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("المسمى الوظيفي"))
    department = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("القسم"))
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees', verbose_name=_("الفرع"))
    hire_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ التعيين"))
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES, default='full_time', verbose_name=_("نوع العقد"))
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الراتب"))
    phone = models.CharField(max_length=20, validators=[egypt_phone], verbose_name=_("رقم الموبايل"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("البريد"))
    emergency_contact = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("للطوارئ"))
    qualifications = models.TextField(blank=True, null=True, verbose_name=_("المؤهلات"))
    skills = models.TextField(blank=True, null=True, verbose_name=_("المهارات"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    attachments = models.JSONField(default=list, blank=True, verbose_name=_("المرفقات"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['full_name']
        verbose_name = _("موظف")
        verbose_name_plural = _("الموظفين")
        indexes = [
            models.Index(fields=['employee_code']),
            models.Index(fields=['full_name']),
            models.Index(fields=['employee_type']),
        ]

    def __str__(self):
        return f"{self.employee_code} - {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.employee_code:
            last = Employee.objects.order_by('created_at').last()
            num = 1 if not last else int(last.employee_code.split('-')[-1]) + 1
            self.employee_code = f"EMP-{num:05d}"
        super().save(*args, **kwargs)


class Attendance(models.Model):
    STATUS = [
        ('present', 'حاضر'),
        ('absent', 'غائب'),
        ('leave', 'إجازة'),
        ('mission', 'مأمورية'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances', verbose_name=_("الموظف"))
    date = models.DateField(verbose_name=_("التاريخ"))
    check_in = models.TimeField(null=True, blank=True, verbose_name=_("وقت الحضور"))
    check_out = models.TimeField(null=True, blank=True, verbose_name=_("وقت الانصراف"))
    status = models.CharField(max_length=20, choices=STATUS, default='present', verbose_name=_("الحالة"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))

    class Meta:
        ordering = ['-date']
        verbose_name = _("حضور")
        verbose_name_plural = _("الحضور والانصراف")
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"


class Task(models.Model):
    PRIORITY = [
        ('high', 'عالية'),
        ('medium', 'متوسطة'),
        ('low', 'منخفضة'),
    ]
    STATUS = [
        ('new', 'جديدة'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'منجزة'),
        ('cancelled', 'ملغاة'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name=_("العنوان"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks', verbose_name=_("مسند إلى"))
    assigned_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tasks', verbose_name=_("مسند من"))
    priority = models.CharField(max_length=20, choices=PRIORITY, default='medium', verbose_name=_("الأولوية"))
    due_date = models.DateField(null=True, blank=True, verbose_name=_("تاريخ التسليم"))
    status = models.CharField(max_length=20, choices=STATUS, default='new', verbose_name=_("الحالة"))
    related_model = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("النموذج المرتبط"))
    related_id = models.UUIDField(null=True, blank=True, verbose_name=_("معرف العنصر"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الإنجاز"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("مهمة")
        verbose_name_plural = _("المهام")

    def __str__(self):
        return self.title
