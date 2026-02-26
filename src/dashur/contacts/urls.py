"""
URL configuration for the contacts app.
"""
from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    # Contact submissions
    path('', views.ContactSubmissionListView.as_view(), name='submission_list_create'),
    path('create/', views.create_contact_submission, name='submission_create'),
    path('<int:pk>/', views.ContactSubmissionDetailView.as_view(), name='submission_detail'),
    
    # Contact responses
    path('responses/', views.ContactResponseListCreateView.as_view(), name='response_list_create'),
    
    # Statistics
    path('stats/', views.contact_stats, name='contact_stats'),
]
