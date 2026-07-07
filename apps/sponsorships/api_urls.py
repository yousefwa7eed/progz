from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'sponsorships', api.SponsorshipViewSet, basename='api_sponsorships')
urlpatterns = router.urls
