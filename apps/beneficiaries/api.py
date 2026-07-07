from rest_framework import serializers, viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Beneficiary


class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = [
            'id', 'code', 'full_name', 'gender', 'birth_date', 'phone', 'phone2',
            'address', 'city', 'district', 'marital_status', 'family_members',
            'has_orphans', 'orphans_count', 'health_status', 'has_chronic_disease',
            'chronic_diseases', 'has_disabilities', 'disabilities_details',
            'employment_status', 'housing_type', 'is_urgent', 'priority_score',
            'branch', 'status', 'notes', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['code', 'priority_score', 'created_at', 'updated_at', 'created_by']


class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.filter(is_active=True).select_related('branch', 'created_by')
    serializer_class = BeneficiarySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'phone', 'code']
    ordering_fields = ['created_at', 'priority_score', 'full_name']
    filterset_fields = ['city', 'marital_status', 'employment_status', 'is_urgent', 'status', 'gender']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def beneficiary_search_api(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return Response({'results': [], 'error': 'حد أدنى 2 أحرف للبحث'}, status=400)
    beneficiaries = Beneficiary.objects.filter(
        Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(code__icontains=q),
        is_active=True
    )[:20]
    results = [{'id': str(b.id), 'text': f'{b.code} - {b.full_name}'} for b in beneficiaries]
    return Response({'results': results})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def beneficiary_quick_add_api(request):
    name = request.data.get('full_name', '').strip()
    gender = request.data.get('gender', '')
    phone = request.data.get('phone', '').strip()
    if not name or not gender or not phone:
        return Response({'error': 'الاسم والجنس ورقم الموبايل مطلوبة'}, status=400)
    if Beneficiary.objects.filter(phone=phone, is_active=True).exists():
        return Response({'error': 'رقم الموبايل موجود مسبقاً'}, status=409)
    b = Beneficiary(full_name=name, gender=gender, phone=phone, created_by=request.user)
    b.save()
    return Response({'id': str(b.id), 'code': b.code, 'name': b.full_name}, status=201)
