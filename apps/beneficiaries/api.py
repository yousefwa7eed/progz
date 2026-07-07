from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Beneficiary


class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = '__all__'


class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.filter(is_active=True)
    serializer_class = BeneficiarySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'phone', 'code', 'national_id']
    ordering_fields = ['created_at', 'priority_score', 'full_name']
