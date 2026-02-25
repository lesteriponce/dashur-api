"""
Wagtail hooks for customizing the admin interface.
"""
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.views.home import HomeView
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


@hooks.register('register_admin_menu_item')
def register_custom_menu_items():
    """Register custom menu items in Wagtail admin."""
    
    # Careers menu item
    return MenuItem(
        _('Careers'),
        reverse('careers:position_list_create'),
        classnames='icon icon-folder-open-inverse',
        order=200
    )


@hooks.register('construct_homepage_panels')
def add_custom_panels(request, panels):
    """Add custom panels to Wagtail admin homepage."""
    
    # Add statistics panel
    from careers.models import JobPosition, JobApplication
    from contacts.models import ContactSubmission
    
    if request.user.is_staff:
        # Get statistics
        active_positions = JobPosition.objects.filter(status='active').count()
        total_applications = JobApplication.objects.count()
        pending_applications = JobApplication.objects.filter(status='pending').count()
        new_contacts = ContactSubmission.objects.filter(status='new').count()
        
        # Create custom panel
        from wagtail.admin.panels import FieldPanel, MultiFieldPanel
        
        panels.append(
            MultiFieldPanel(
                [
                    FieldPanel('active_positions', heading=f'Active Positions: {active_positions}'),
                    FieldPanel('total_applications', heading=f'Total Applications: {total_applications}'),
                    FieldPanel('pending_applications', heading=f'Pending Applications: {pending_applications}'),
                    FieldPanel('new_contacts', heading=f'New Contacts: {new_contacts}'),
                ],
                heading=_('Dashboard Statistics'),
                classname='collapsible'
            )
        )
