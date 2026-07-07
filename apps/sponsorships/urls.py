from django.urls import path
from . import views

urlpatterns = [
    path('', views.SponsorshipListView.as_view(), name='sponsorship_list'),
    path('add/', views.SponsorshipCreateView.as_view(), name='sponsorship_add'),
    path('<uuid:pk>/', views.SponsorshipDetailView.as_view(), name='sponsorship_detail'),
]
