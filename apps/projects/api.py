from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'code', 'name', 'project_type', 'description',
            'goal_amount', 'total_budget', 'total_spent',
            'start_date', 'end_date', 'status', 'manager',
            'beneficiaries_count', 'locations', 'notes', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['code', 'total_spent', 'approved_by', 'created_at', 'updated_at', 'created_by']


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().select_related('manager', 'approved_by', 'created_by')
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name']
    filterset_fields = ['status', 'project_type', 'is_active']
    ordering_fields = ['created_at', 'start_date', 'goal_amount', 'total_budget']
