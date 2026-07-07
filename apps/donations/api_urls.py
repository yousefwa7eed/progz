from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'donations', api.DonationViewSet, basename='api_donations')
urlpatterns = router.urls
