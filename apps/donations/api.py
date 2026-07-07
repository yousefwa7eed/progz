from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Donation


class DonationSerializer(serializers.ModelSerializer):
    donor_name_field = serializers.CharField(source='donor.full_name', read_only=True)

    class Meta:
        model = Donation
        fields = [
            'id', 'code', 'donor', 'donor_name_field', 'donor_name', 'donation_type',
            'payment_method', 'amount', 'currency', 'items', 'transaction_type',
            'campaign', 'project', 'branch', 'receipt_number', 'receipt_date',
            'is_anonymous', 'is_zakat', 'zakat_year', 'notes', 'status',
            'is_deposited', 'deposited_date', 'created_at', 'updated_at',
        ]
        read_only_fields = ['code', 'receipt_number', 'receipt_date', 'created_at', 'updated_at', 'created_by', 'received_by']


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all().select_related('donor', 'project', 'branch', 'received_by', 'created_by')
    serializer_class = DonationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'receipt_number', 'donor__full_name', 'donor_name']
    ordering_fields = ['created_at', 'amount', 'receipt_date']
    filterset_fields = ['donation_type', 'transaction_type', 'status', 'is_zakat', 'is_deposited', 'payment_method']
