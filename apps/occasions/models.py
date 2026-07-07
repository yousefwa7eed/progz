import uuid
from django.db import models
from django.utils import timezone


class Occasion(models.Model):
    SUPPORT_TYPES = [
        ('food', 'دعم غذائي'),
        ('financial', 'دعم مالي'),
        ('cloth', 'كسوة'),
        ('medical', 'علاج'),
        ('educational', 'دعم تعليمي'),
        ('housing', 'ترميم/إسكان'),
        ('other', 'أخرى'),
    ]
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('completed', 'منتهي'),
        ('cancelled', 'ملغي'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='اسم المناسبة')
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    support_type = models.CharField(max_length=50, choices=SUPPORT_TYPES, default='food', verbose_name='نوع الدعم')
    custom_support_type = models.CharField(max_length=255, blank=True, null=True, verbose_name='نوع الدعم (مخصص)')
    budget_enabled = models.BooleanField(default=False, verbose_name='بميزانية')
    budget_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='الميزانية')
    start_date = models.DateField(default=timezone.now, verbose_name='تاريخ البداية')
    end_date = models.DateField(null=True, blank=True, verbose_name='تاريخ النهاية')
    is_recurring = models.BooleanField(default=False, verbose_name='موسم سنوي')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='created_occasions', verbose_name='أضيف بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'مناسبة'
        verbose_name_plural = 'المناسبات والمواسم'

    def __str__(self):
        return self.name

    @property
    def display_support_type(self):
        if self.support_type == 'other' and self.custom_support_type:
            return self.custom_support_type
        return dict(self.SUPPORT_TYPES).get(self.support_type, '')

    @property
    def member_count(self):
        return self.members.count()


class OccasionMember(models.Model):
    MEMBER_TYPES = [
        ('case', 'حالة'),
        ('beneficiary', 'مستفيد'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    occasion = models.ForeignKey(Occasion, on_delete=models.CASCADE, related_name='members', verbose_name='المناسبة')
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPES, verbose_name='النوع')
    case = models.ForeignKey('cases.Case', on_delete=models.SET_NULL, null=True, blank=True, related_name='occasion_members', verbose_name='الحالة')
    beneficiary = models.ForeignKey('beneficiaries.Beneficiary', on_delete=models.SET_NULL, null=True, blank=True, related_name='occasion_members', verbose_name='المستفيد')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    completed = models.BooleanField(default=False, verbose_name='تم')
    added_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, verbose_name='أضيف بواسطة')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added_at']
        verbose_name = 'عضو مناسبة'
        verbose_name_plural = 'أعضاء المناسبات'

    def __str__(self):
        if self.member_type == 'case' and self.case:
            return f'{self.case.code} - {self.case.beneficiary.full_name}'
        if self.beneficiary:
            return self.beneficiary.full_name
        return str(self.id)

    @property
    def display_name(self):
        if self.member_type == 'case' and self.case:
            return f'{self.case.beneficiary.full_name} ({self.case.code})'
        if self.beneficiary:
            return self.beneficiary.full_name
        return '-'

    @property
    def pending_tasks_count(self):
        return self.tasks.exclude(status='completed').count()

    @property
    def completed_tasks_count(self):
        return self.tasks.filter(status='completed').count()


class OccasionTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('completed', 'تم'),
        ('cancelled', 'ملغي'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(OccasionMember, on_delete=models.CASCADE, related_name='tasks', verbose_name='العضو')
    task_name = models.CharField(max_length=255, verbose_name='المهمة')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الإنجاز')
    completed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_tasks', verbose_name='أنجز بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'مهمة'
        verbose_name_plural = 'المهام'

    def __str__(self):
        return self.task_name
