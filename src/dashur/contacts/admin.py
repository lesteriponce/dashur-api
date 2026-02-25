"""
Admin configuration for the contacts app.
"""
from django.contrib import admin
from .models import ContactSubmission, ContactResponse


class ContactResponseInline(admin.TabularInline):
    model = ContactResponse
    extra = 0
    readonly_fields = ('created_at', 'responded_by')
    fields = ('response_message', 'response_email_sent', 'responded_by', 'created_at')


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'newsletter_subscription', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
    list_editable = ('status', 'priority')
    ordering = ('-created_at',)
    inlines = [ContactResponseInline]
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'company')
        }),
        ('Submission Details', {
            'fields': ('subject', 'message', 'priority', 'status')
        }),
        ('Additional Information', {
            'fields': ('referral_source', 'newsletter_subscription', 'ip_address', 'user_agent')
        }),
        ('Internal Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('ip_address', 'user_agent', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('response')


@admin.register(ContactResponse)
class ContactResponseAdmin(admin.ModelAdmin):
    list_display = ('submission', 'responded_by', 'response_email_sent', 'created_at')
    list_filter = ('response_email_sent', 'created_at')
    search_fields = ('submission__subject', 'submission__email', 'response_message')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Response Details', {
            'fields': ('submission', 'response_message', 'response_email_sent')
        }),
        ('Metadata', {
            'fields': ('responded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('responded_by', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('submission', 'responded_by')
