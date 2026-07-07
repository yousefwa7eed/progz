from django.urls import path
from . import views

urlpatterns = [
    path('', views.CaseListView.as_view(), name='case_list'),
    path('add/', views.CaseCreateView.as_view(), name='case_add'),
    path('<uuid:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('<uuid:pk>/approve/', views.case_approve, name='case_approve'),
    path('<uuid:pk>/reject/', views.case_reject, name='case_reject'),
    path('<uuid:pk>/disburse/', views.case_disburse, name='case_disburse'),
    path('<uuid:pk>/add-image/', views.case_add_image, name='case_add_image'),
    path('<uuid:pk>/delete-image/<uuid:image_id>/', views.case_delete_image, name='case_delete_image'),
    path('<uuid:pk>/add-feature/', views.case_add_feature, name='case_add_feature'),
    path('<uuid:pk>/delete-feature/<uuid:feature_id>/', views.case_delete_feature, name='case_delete_feature'),
    path('type/<str:case_type>/', views.case_type_view, name='case_type_view'),
    path('type/<str:case_type>/export/', views.case_type_export_excel, name='case_type_export'),
]
