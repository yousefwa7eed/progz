from django.urls import path
from . import views

urlpatterns = [
    path('', views.FinanceDashboardView.as_view(), name='finance_dashboard'),
    path('entries/', views.EntryListView.as_view(), name='entry_list'),
    path('entries/add/', views.EntryCreateView.as_view(), name='entry_add'),
    path('entries/<uuid:pk>/', views.EntryDetailView.as_view(), name='entry_detail'),
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
]
