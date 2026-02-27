"""
URL configuration for CMS app.
"""
from django.urls import path
from . import views

app_name = 'cms_auth'

urlpatterns = [
    path('login/', views.cms_login_view, name='cms_login'),
    path('dashboard/', views.cms_dashboard_view, name='cms_dashboard'),
    path('profile/', views.cms_profile_view, name='cms_profile'),
    path('logout/', views.cms_logout_view, name='cms_logout'),
    path('revoke-session/<str:session_key>/', views.cms_revoke_session_view, name='cms_revoke_session'),
    path('access-denied/', views.cms_access_denied_view, name='cms_access_denied'),
]
