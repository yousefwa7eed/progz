from django.urls import path
from . import views

urlpatterns = [
    path('', views.EmployeeListView.as_view(), name='employee_list'),
    path('add/', views.EmployeeCreateView.as_view(), name='employee_add'),
    path('<uuid:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
]
