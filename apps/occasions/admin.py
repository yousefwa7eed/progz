from django.contrib import admin
from .models import Occasion, OccasionMember, OccasionTask

@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ['name', 'support_type', 'status', 'member_count', 'start_date', 'end_date']
    list_filter = ['status', 'support_type', 'is_recurring']

@admin.register(OccasionMember)
class OccasionMemberAdmin(admin.ModelAdmin):
    list_display = ['occasion', 'display_name', 'member_type', 'completed', 'added_at']
    list_filter = ['member_type', 'completed']

@admin.register(OccasionTask)
class OccasionTaskAdmin(admin.ModelAdmin):
    list_display = ['task_name', 'member', 'status', 'completed_at']
    list_filter = ['status']
