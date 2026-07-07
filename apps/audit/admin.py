from django.contrib import admin
from .models import AuditLog, Notification, BackupLog, SystemSetting

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor', 'model_name', 'model_id', 'ip_address', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('actor__username', 'model_name', 'ip_address')
    readonly_fields = ('timestamp',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')

@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_size', 'status', 'backup_type', 'created_at')
    list_filter = ('status', 'backup_type')

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'is_encrypted', 'updated_at')
    search_fields = ('key',)
