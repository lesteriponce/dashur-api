"""
Admin URL configuration for the careers app.
Uses SessionAuthentication for file uploads and traditional web forms.
"""
from django.urls import path
from . import views

app_name = 'careers_admin'

urlpatterns = [
    # Job application management with file uploads (SessionAuthentication)
    path('applications/', views.JobApplicationListCreateView.as_view(), name='application_list_create_admin'),
    path('applications/<int:pk>/', views.JobApplicationDetailView.as_view(), name='application_detail_admin'),
]
