from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Project, ProjectPhase

class ProjectPhaseInline(admin.TabularInline):
    model = ProjectPhase
    extra = 0

@admin.register(Project)
class ProjectAdmin(SimpleHistoryAdmin):
    list_display = ('code', 'name', 'project_type', 'status', 'manager', 'total_budget', 'start_date')
    list_filter = ('status', 'project_type', 'is_active')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('code', 'total_spent', 'created_at')
    inlines = [ProjectPhaseInline]

@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'status', 'budget', 'spent', 'start_date', 'end_date')
    list_filter = ('status',)
