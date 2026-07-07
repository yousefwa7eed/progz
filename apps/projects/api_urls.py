from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'projects', api.ProjectViewSet, basename='api_projects')
urlpatterns = router.urls
