from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'inventory/items', api.InventoryItemViewSet, basename='api_inventory')
urlpatterns = router.urls
