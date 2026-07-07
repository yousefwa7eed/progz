from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'beneficiaries', api.BeneficiaryViewSet, basename='api_beneficiaries')
urlpatterns = router.urls
