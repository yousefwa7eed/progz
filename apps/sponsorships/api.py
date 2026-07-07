from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Sponsorship


class SponsorshipSerializer(serializers.ModelSerializer):
    sponsor_name = serializers.CharField(source='sponsor.full_name', read_only=True)
    beneficiary_name = serializers.CharField(source='beneficiary.full_name', read_only=True)

    class Meta:
        model = Sponsorship
        fields = [
            'id', 'code', 'sponsor', 'sponsor_name', 'beneficiary', 'beneficiary_name',
            'sponsorship_type', 'monthly_amount', 'start_date', 'end_date',
            'duration_months', 'is_permanent', 'payment_method', 'payment_day',
            'is_active', 'status', 'last_payment_date', 'next_payment_date',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['code', 'total_paid', 'last_payment_date', 'next_payment_date', 'created_at', 'updated_at', 'created_by']


class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all().select_related('sponsor', 'beneficiary', 'created_by')
    serializer_class = SponsorshipSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'sponsor__full_name', 'beneficiary__full_name']
    filterset_fields = ['sponsorship_type', 'status', 'is_active', 'payment_method']
    ordering_fields = ['created_at', 'monthly_amount', 'start_date', 'total_paid']
