from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Beneficiary

@admin.register(Beneficiary)
class BeneficiaryAdmin(SimpleHistoryAdmin):
    list_display = ('code', 'full_name', 'phone', 'city', 'is_urgent', 'priority_score', 'status')
    list_filter = ('status', 'is_urgent', 'gender', 'marital_status', 'city', 'branch')
    search_fields = ('code', 'full_name', 'phone', 'national_id')
    readonly_fields = ('code', 'priority_score', 'created_at', 'updated_at')
