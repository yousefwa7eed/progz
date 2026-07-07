from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Donor


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = '__all__'


class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.filter(is_active=True)
    serializer_class = DonorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'phone', 'code', 'email']
    ordering_fields = ['total_donations', 'created_at', 'full_name']
