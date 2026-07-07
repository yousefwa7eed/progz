from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = '__all__'


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.filter(is_active=True)
    serializer_class = InventoryItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['code', 'name']
    filterset_fields = ['category']
