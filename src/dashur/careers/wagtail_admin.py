"""
Wagtail admin customization for careers app.
"""
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import JobPosition, JobApplication


class JobPositionModelAdmin(ModelAdmin):
    """ModelAdmin for JobPosition."""
    model = JobPosition
    menu_label = 'Job Positions'
    menu_icon = 'folder-open-inverse'
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    
    list_display = ('title', 'department', 'employment_type', 'status', 'created_at')
    list_filter = ('status', 'employment_type', 'department', 'created_at')
    search_fields = ('title', 'department', 'description')
    ordering = ('-created_at')
    
    panels = [
        ('Basic Information', {
            'fields': ('title', 'department', 'employment_type', 'status')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'responsibilities', 'benefits')
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max', 'location', 'remote_work')
        }),
        ('Requirements', {
            'fields': ('experience_years', 'education_level', 'application_deadline')
        }),
        ('Settings', {
            'fields': ('is_featured',)
        }),
    ]


class JobApplicationModelAdmin(ModelAdmin):
    """ModelAdmin for JobApplication."""
    model = JobApplication
    menu_label = 'Applications'
    menu_icon = 'folder'
    menu_order = 210
    add_to_settings_menu = False
    exclude_from_explorer = False
    
    list_display = ('full_name', 'position', 'status', 'email', 'applied_at')
    list_filter = ('status', 'position__department', 'applied_at')
    search_fields = ('first_name', 'last_name', 'email', 'position__title')
    ordering = ('-applied_at')
    
    panels = [
        ('Applicant Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Application Details', {
            'fields': ('position', 'resume', 'cover_letter', 'status')
        }),
        ('Additional Information', {
            'fields': ('linkedin_profile', 'portfolio', 'expected_salary', 'available_start_date')
        }),
        ('Internal Notes', {
            'fields': ('notes',)
        }),
    ]


# Register the ModelAdmin classes
modeladmin_register(JobPositionModelAdmin)
modeladmin_register(JobApplicationModelAdmin)
