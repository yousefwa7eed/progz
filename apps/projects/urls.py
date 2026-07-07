from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('add/', views.ProjectCreateView.as_view(), name='project_add'),
    path('<uuid:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<uuid:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
]
