from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'beneficiaries', api.BeneficiaryViewSet, basename='api_beneficiaries')

urlpatterns = router.urls + [
    path('beneficiaries/search/', api.beneficiary_search_api, name='api_beneficiary_search'),
    path('beneficiaries/quick-add/', api.beneficiary_quick_add_api, name='api_beneficiary_quick_add'),
]
