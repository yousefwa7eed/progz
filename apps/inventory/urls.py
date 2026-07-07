from django.urls import path
from . import views

urlpatterns = [
    path('', views.InventoryListView.as_view(), name='inventory_list'),
    path('items/add/', views.ItemCreateView.as_view(), name='item_add'),
    path('items/<uuid:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='transaction_add'),
]
