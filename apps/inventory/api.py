from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'code', 'name', 'category', 'unit', 'quantity',
            'min_quantity', 'max_quantity', 'expiry_date', 'location',
            'notes', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['code', 'created_at', 'updated_at']


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.filter(is_active=True).select_related('category')
    serializer_class = InventoryItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name']
    filterset_fields = ['category', 'is_active']
    ordering_fields = ['name', 'quantity', 'created_at']
