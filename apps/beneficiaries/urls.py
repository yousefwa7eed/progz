from django.urls import path
from . import views

urlpatterns = [
    path('', views.BeneficiaryListView.as_view(), name='beneficiary_list'),
    path('add/', views.BeneficiaryCreateView.as_view(), name='beneficiary_add'),
    path('<uuid:pk>/', views.BeneficiaryDetailView.as_view(), name='beneficiary_detail'),
    path('<uuid:pk>/edit/', views.BeneficiaryUpdateView.as_view(), name='beneficiary_edit'),
    path('search/', views.beneficiary_search, name='beneficiary_search'),
]
