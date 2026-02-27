"""
Admin configuration for the authentication app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, AdminUser, CMSUser, CMSSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_verified', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'website', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'location')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Profile Information', {'fields': ('bio', 'avatar', 'location')}),
        ('Social Links', {'fields': ('website', 'linkedin', 'github')}),
        ('Documents', {'fields': ('resume',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_super_admin', 'is_active', 'created_at')
    list_filter = ('is_super_admin', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Admin Permissions', {'fields': ('is_super_admin',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CMSUser)
class CMSUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_content_manager', 'is_api_viewer', 'is_active', 'created_at')
    list_filter = ('is_content_manager', 'is_api_viewer', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('CMS Permissions', {'fields': ('is_content_manager', 'is_api_viewer')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CMSSession)
class CMSSessionAdmin(admin.ModelAdmin):
    list_display = ('cms_user', 'ip_address', 'is_active', 'created_at', 'last_activity')
    list_filter = ('is_active', 'created_at', 'last_activity')
    search_fields = ('cms_user__user__email', 'ip_address', 'session_key')
    ordering = ('-last_activity',)
    
    fieldsets = (
        (None, {'fields': ('cms_user',)}),
        ('Session Information', {'fields': ('session_key', 'ip_address', 'user_agent')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'last_activity')}),
    )
    
    readonly_fields = ('cms_user', 'session_key', 'ip_address', 'user_agent', 'created_at', 'last_activity')
