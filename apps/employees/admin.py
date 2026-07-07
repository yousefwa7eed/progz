from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Employee, Attendance, Task

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0

@admin.register(Employee)
class EmployeeAdmin(SimpleHistoryAdmin):
    list_display = ('employee_code', 'full_name', 'employee_type', 'position', 'department', 'phone', 'is_active')
    list_filter = ('employee_type', 'department', 'is_active', 'branch')
    search_fields = ('employee_code', 'full_name', 'phone', 'email')
    readonly_fields = ('employee_code', 'created_at')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status')
    list_filter = ('status', 'date')
    search_fields = ('employee__full_name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'priority', 'status', 'due_date')
    list_filter = ('status', 'priority')
    search_fields = ('title',)
