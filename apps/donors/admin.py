from django.contrib import admin
from .models import Donor, DonorCategory

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('code', 'full_name', 'donor_type', 'phone', 'total_donations', 'is_committed')
    list_filter = ('donor_type', 'is_committed', 'is_active', 'city')
    search_fields = ('code', 'full_name', 'phone', 'email')
    readonly_fields = ('code', 'total_donations', 'last_donation_date', 'created_at')

@admin.register(DonorCategory)
class DonorCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')
