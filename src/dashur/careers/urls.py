"""
URL configuration for the careers app.
JWT authentication for API endpoints.
"""
from django.urls import path
from . import views

app_name = 'careers'

urlpatterns = [
    # Job positions (JWT Authentication)
    path('positions/', views.JobPositionListCreateView.as_view(), name='position_list_create'),
    path('positions/<int:pk>/', views.JobPositionDetailView.as_view(), name='position_detail'),
    
    # Job applications - read-only via API (JWT Authentication)
    path('applications/my/', views.my_applications, name='my_applications'),
    path('applications/', views.JobApplicationListCreateView.as_view(), name='application_list_create'),
    
    # Statistics (JWT Authentication)
    path('stats/', views.application_stats, name='application_stats'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/activity/', views.recent_activity, name='recent_activity'),
]
