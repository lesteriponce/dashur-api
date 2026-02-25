"""
Wagtail admin customization for contacts app.
"""
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import ContactSubmission, ContactResponse


class ContactSubmissionModelAdmin(ModelAdmin):
    """ModelAdmin for ContactSubmission."""
    model = ContactSubmission
    menu_label = 'Contact Submissions'
    menu_icon = 'mail'
    menu_order = 220
    add_to_settings_menu = False
    exclude_from_explorer = False
    
    list_display = ('full_name', 'email', 'subject', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'newsletter_subscription', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
    ordering = ('-created_at')
    
    panels = [
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
    ]


class ContactResponseModelAdmin(ModelAdmin):
    """ModelAdmin for ContactResponse."""
    model = ContactResponse
    menu_label = 'Contact Responses'
    menu_icon = 'tick'
    menu_order = 230
    add_to_settings_menu = False
    exclude_from_explorer = False
    
    list_display = ('submission', 'responded_by', 'response_email_sent', 'created_at')
    list_filter = ('response_email_sent', 'created_at')
    search_fields = ('submission__subject', 'submission__email', 'response_message')
    ordering = ('-created_at')
    
    panels = [
        ('Response Details', {
            'fields': ('submission', 'response_message', 'response_email_sent')
        }),
        ('Metadata', {
            'fields': ('responded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]


# Register the ModelAdmin classes
modeladmin_register(ContactSubmissionModelAdmin)
modeladmin_register(ContactResponseModelAdmin)
