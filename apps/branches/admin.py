from django.contrib import admin
from .models import Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'phone', 'is_active')
    search_fields = ('code', 'name', 'city')
