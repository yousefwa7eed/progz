from django.contrib import admin
from .models import Sponsorship, SponsorshipPayment

class SponsorshipPaymentInline(admin.TabularInline):
    model = SponsorshipPayment
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ('code', 'sponsor', 'beneficiary', 'sponsorship_type', 'monthly_amount', 'status', 'next_payment_date')
    list_filter = ('sponsorship_type', 'status', 'is_active')
    search_fields = ('code', 'sponsor__full_name', 'beneficiary__full_name')
    readonly_fields = ('code', 'total_paid', 'last_payment_date', 'created_at')
    inlines = [SponsorshipPaymentInline]

@admin.register(SponsorshipPayment)
class SponsorshipPaymentAdmin(admin.ModelAdmin):
    list_display = ('sponsorship', 'amount', 'payment_date', 'month', 'year')
    list_filter = ('payment_date',)
