from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'donors', api.DonorViewSet, basename='api_donors')
urlpatterns = router.urls
