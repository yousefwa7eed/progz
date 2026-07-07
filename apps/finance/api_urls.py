from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'finance/entries', api.FinancialEntryViewSet, basename='api_entries')
router.register(r'finance/accounts', api.AccountViewSet, basename='api_accounts')
urlpatterns = router.urls
