from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, Permission

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'full_name', 'role', 'phone', 'email', 'is_active', 'otp_enabled')
    list_filter = ('role', 'is_active', 'otp_enabled')
    search_fields = ('username', 'full_name', 'phone', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('معلومات شخصية', {'fields': ('full_name', 'phone', 'email', 'national_id')}),
        ('الصلاحيات', {'fields': ('role', 'extra_permissions', 'is_active', 'is_staff', 'is_superuser')}),
        ('الأمان', {'fields': ('otp_enabled', 'otp_secret')}),
        ('تواريخ', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'priority', 'is_system')
    search_fields = ('name', 'code')

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'module')
    list_filter = ('module',)
    search_fields = ('name', 'codename', 'module')
