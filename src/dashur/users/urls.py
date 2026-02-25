"""
URL configuration for the users app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'activities', views.UserActivityViewSet, basename='user-activity')
router.register(r'sessions', views.UserSessionViewSet, basename='user-session')
router.register(r'preferences', views.UserPreferenceViewSet, basename='user-preference')

app_name = 'users'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Direct views
    path('api/activity-log/', views.UserActivityListView.as_view(), name='user-activity-list'),
    path('api/preferences/', views.UserPreferenceView.as_view(), name='user-preferences'),
]
