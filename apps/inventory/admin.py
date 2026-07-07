from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import InventoryCategory, InventoryItem, InventoryTransaction

class InventoryTransactionInline(admin.TabularInline):
    model = InventoryTransaction
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')

@admin.register(InventoryItem)
class InventoryItemAdmin(SimpleHistoryAdmin):
    list_display = ('code', 'name', 'category', 'quantity', 'min_quantity', 'unit', 'location')
    list_filter = ('category', 'is_active')
    search_fields = ('code', 'name')
    readonly_fields = ('quantity', 'code')
    inlines = [InventoryTransactionInline]

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('item', 'transaction_type', 'quantity', 'performed_by', 'created_at')
    list_filter = ('transaction_type', 'created_at')
