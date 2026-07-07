from rest_framework import serializers, viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import Case


class CaseSerializer(serializers.ModelSerializer):
    beneficiary_name = serializers.CharField(source='beneficiary.full_name', read_only=True)

    class Meta:
        model = Case
        fields = [
            'id', 'code', 'beneficiary', 'beneficiary_name', 'case_type', 'priority',
            'description', 'requested_amount', 'approved_amount', 'status',
            'assigned_to', 'needs_reassessment', 'reassessment_date',
            'close_reason', 'notes', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['code', 'reviewed_by', 'approved_by', 'reviewed_at', 'approved_at', 'closed_at', 'created_at', 'updated_at', 'created_by']


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all().select_related('beneficiary', 'assigned_to', 'created_by')
    serializer_class = CaseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'beneficiary__full_name', 'description']
    filterset_fields = ['status', 'priority', 'case_type']
    ordering_fields = ['created_at', 'requested_amount', 'approved_amount', 'priority']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def case_search_api(request):
    q = request.GET.get('q', '').strip()
    cases = Case.objects.select_related('beneficiary').filter(
        status__in=['new', 'under_study', 'approved']
    )
    if q:
        if len(q) < 2:
            return Response({'results': [], 'error': 'حد أدنى 2 أحرف للبحث'}, status=400)
        cases = cases.filter(
            models.Q(code__icontains=q) |
            models.Q(beneficiary__full_name__icontains=q) |
            models.Q(beneficiary__phone__icontains=q)
        )
    results = [{
        'id': str(c.id),
        'text': f'{c.beneficiary.full_name} ({c.code}) - {c.get_case_type_display()}',
    } for c in cases[:50]]
    return Response({'results': results})
