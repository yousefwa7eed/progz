from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import FinancialEntry, Account


class FinancialEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialEntry
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class FinancialEntryViewSet(viewsets.ModelViewSet):
    queryset = FinancialEntry.objects.all()
    serializer_class = FinancialEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['entry_type', 'transaction_type', 'is_approved']


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.filter(is_active=True)
    serializer_class = AccountSerializer
