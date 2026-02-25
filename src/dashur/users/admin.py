"""
Admin configuration for the users app.
"""
from django.contrib import admin
from .models import UserActivity, UserSession, UserPreference


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'action', 'description')
    ordering = ('-timestamp',)
    readonly_fields = ('user', 'action', 'description', 'ip_address', 'user_agent', 'timestamp')
    
    def has_add_permission(self, request):
        return False  # Activities should be created programmatically


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key_short', 'ip_address', 'is_active', 'last_activity')
    list_filter = ('is_active', 'last_activity')
    search_fields = ('user__email', 'ip_address')
    ordering = ('-last_activity',)
    readonly_fields = ('user', 'session_key', 'ip_address', 'user_agent', 'created_at', 'last_activity')
    
    def session_key_short(self, obj):
        return obj.session_key[:8] + '...' if obj.session_key else ''
    session_key_short.short_description = 'Session Key'
    
    def has_add_permission(self, request):
        return False  # Sessions should be created programmatically


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'timezone', 'email_notifications', 'theme')
    list_filter = ('language', 'timezone', 'email_notifications', 'push_notifications', 'theme')
    search_fields = ('user__email',)
    ordering = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
