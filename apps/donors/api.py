from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Donor


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = [
            'id', 'code', 'full_name', 'donor_type', 'phone', 'email',
            'address', 'city', 'commercial_reg', 'contact_person',
            'preferred_contact', 'preferred_donation', 'is_anonymous',
            'is_committed', 'last_donation_date', 'donor_category',
            'notes', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['code', 'total_donations', 'last_donation_date', 'created_at', 'updated_at', 'created_by']


class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.filter(is_active=True).select_related('donor_category', 'created_by')
    serializer_class = DonorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'phone', 'code', 'email']
    ordering_fields = ['total_donations', 'created_at', 'full_name']
    filterset_fields = ['donor_type', 'city', 'is_anonymous', 'is_committed', 'donor_category']
