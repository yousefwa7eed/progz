from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import FinancialEntry, Account


class FinancialEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialEntry
        fields = [
            'id', 'code', 'entry_type', 'entry_date', 'amount', 'currency',
            'description', 'account', 'donor', 'donation', 'expense_category',
            'project', 'case', 'payment_method', 'reference_number',
            'receipt_number', 'is_approved', 'transaction_type',
            'is_reconciled', 'notes', 'created_at',
        ]
        read_only_fields = ['code', 'is_approved', 'approved_by', 'recorded_by', 'created_at', 'updated_at']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id', 'code', 'name', 'account_type', 'parent',
            'account_group', 'opening_balance', 'is_active', 'notes', 'created_at',
        ]
        read_only_fields = ['current_balance', 'created_at']


class FinancialEntryViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch']
    queryset = FinancialEntry.objects.all().select_related(
        'account', 'donor', 'donation', 'expense_category', 'project', 'case',
        'bank_account', 'approved_by', 'recorded_by'
    )
    serializer_class = FinancialEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['code', 'description', 'reference_number', 'receipt_number']
    ordering_fields = ['entry_date', 'amount', 'created_at']
    filterset_fields = ['entry_type', 'transaction_type', 'is_approved', 'is_reconciled', 'payment_method']


class AccountViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    queryset = Account.objects.filter(is_active=True).select_related('parent')
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name']
    filterset_fields = ['account_type', 'account_group', 'is_active']
    ordering_fields = ['code', 'name']
