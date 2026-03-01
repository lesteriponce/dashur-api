"""
URL configuration for authentication app.
"""
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # User authentication (JWT)
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('password/change/', views.change_password, name='change_password'),
    path('me/', views.user_info, name='user_info'),
    
    # CMS authentication (Session-based)
    path('cms/login/', views.cms_login, name='cms_login'),
    path('cms/logout/', views.cms_logout, name='cms_logout'),
    path('cms/profile/', views.cms_profile, name='cms_profile'),
    path('cms/sessions/', views.cms_sessions, name='cms_sessions'),
    path('cms/sessions/<str:session_key>/revoke/', views.cms_revoke_session, name='cms_revoke_session'),
]
