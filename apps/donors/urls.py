from django.urls import path
from . import views

urlpatterns = [
    path('', views.DonorListView.as_view(), name='donor_list'),
    path('add/', views.DonorCreateView.as_view(), name='donor_add'),
    path('<uuid:pk>/', views.DonorDetailView.as_view(), name='donor_detail'),
    path('<uuid:pk>/edit/', views.DonorUpdateView.as_view(), name='donor_edit'),
]
