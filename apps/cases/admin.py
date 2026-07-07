from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Case, CaseActivity

class CaseActivityInline(admin.TabularInline):
    model = CaseActivity
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Case)
class CaseAdmin(SimpleHistoryAdmin):
    list_display = ('code', 'beneficiary', 'case_type', 'priority', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'case_type', 'created_at')
    search_fields = ('code', 'beneficiary__full_name', 'description')
    readonly_fields = ('code', 'created_at', 'updated_at')
    inlines = [CaseActivityInline]

@admin.register(CaseActivity)
class CaseActivityAdmin(admin.ModelAdmin):
    list_display = ('case', 'activity_type', 'performed_by', 'created_at')
    list_filter = ('activity_type', 'created_at')
