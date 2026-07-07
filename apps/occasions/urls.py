from django.urls import path
from . import views

urlpatterns = [
    path('', views.occasion_list, name='occasion_list'),
    path('add/', views.occasion_create, name='occasion_add'),
    path('<uuid:pk>/', views.occasion_detail, name='occasion_detail'),
    path('<uuid:pk>/edit/', views.occasion_edit, name='occasion_edit'),
    path('<uuid:pk>/delete/', views.occasion_delete, name='occasion_delete'),
    path('<uuid:pk>/add-members/', views.occasion_add_members, name='occasion_add_members'),
    path('<uuid:pk>/remove-member/<uuid:member_pk>/', views.occasion_remove_member, name='occasion_remove_member'),
    path('<uuid:pk>/toggle-member/<uuid:member_pk>/', views.member_toggle_complete, name='member_toggle_complete'),
    path('<uuid:pk>/member/<uuid:member_pk>/add-task/', views.task_add, name='task_add'),
    path('<uuid:pk>/member/<uuid:member_pk>/toggle-task/<uuid:task_pk>/', views.task_toggle, name='task_toggle'),
    path('<uuid:pk>/member/<uuid:member_pk>/delete-task/<uuid:task_pk>/', views.task_delete, name='task_delete'),
    path('<uuid:pk>/export/pdf/', views.occasion_export_pdf, name='occasion_export_pdf'),
    path('<uuid:pk>/export/excel/', views.occasion_export_excel, name='occasion_export_excel'),
    path('api/search-cases/', views.api_search_cases, name='api_search_cases'),
    path('api/search-beneficiaries/', views.api_search_beneficiaries, name='api_search_beneficiaries'),
]
