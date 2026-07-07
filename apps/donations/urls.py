from django.urls import path
from . import views

urlpatterns = [
    path('', views.DonationListView.as_view(), name='donation_list'),
    path('add/', views.DonationCreateView.as_view(), name='donation_add'),
    path('<uuid:pk>/', views.DonationDetailView.as_view(), name='donation_detail'),
    path('<uuid:pk>/receipt/', views.donation_receipt, name='donation_receipt'),
]
