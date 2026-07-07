from django.contrib import admin
from .models import Donation, DonationItem

class DonationItemInline(admin.TabularInline):
    model = DonationItem
    extra = 0

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('code', 'receipt_number', 'donor', 'amount', 'donation_type', 'transaction_type', 'status')
    list_filter = ('donation_type', 'transaction_type', 'status', 'receipt_date')
    search_fields = ('code', 'receipt_number', 'donor__full_name', 'donor_name')
    readonly_fields = ('code', 'receipt_number', 'created_at')
    inlines = [DonationItemInline]
