from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Account, ExpenseCategory, BankAccount, FinancialEntry

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'account_group', 'account_type', 'current_balance', 'is_active')
    list_filter = ('account_group', 'account_type', 'is_active')
    search_fields = ('code', 'name')

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'is_active')
    search_fields = ('code', 'name')

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_name', 'account_number', 'iban', 'current_balance', 'is_active')

@admin.register(FinancialEntry)
class FinancialEntryAdmin(SimpleHistoryAdmin):
    list_display = ('code', 'entry_type', 'amount', 'entry_date', 'account', 'is_approved', 'transaction_type')
    list_filter = ('entry_type', 'is_approved', 'transaction_type', 'entry_date', 'payment_method')
    search_fields = ('code', 'description', 'reference_number')
    readonly_fields = ('code', 'created_at')
