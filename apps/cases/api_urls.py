from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'cases', api.CaseViewSet, basename='api_cases')
urlpatterns = router.urls
