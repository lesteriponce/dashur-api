"""
Admin configuration for the careers app.
"""
from django.contrib import admin
from .models import JobPosition, JobApplication, ApplicationStatusHistory


@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'employment_type', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'employment_type', 'department', 'remote_work', 'is_featured', 'created_at')
    search_fields = ('title', 'department', 'description')
    list_editable = ('status', 'is_featured')
    ordering = ('-created_at',)
    
    fieldsets = (
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
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related().prefetch_related('applications')


class ApplicationStatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ('changed_at', 'changed_by')
    fields = ('old_status', 'new_status', 'changed_by', 'notes', 'changed_at')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'status', 'email', 'applied_at')
    list_filter = ('status', 'position__department', 'applied_at', 'position__employment_type')
    search_fields = ('first_name', 'last_name', 'email', 'position__title')
    list_editable = ('status',)
    ordering = ('-applied_at',)
    inlines = [ApplicationStatusHistoryInline]
    
    fieldsets = (
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
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('applied_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'position')


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('application', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('new_status', 'old_status', 'changed_at')
    search_fields = ('application__first_name', 'application__last_name', 'application__position__title')
    ordering = ('-changed_at',)
    readonly_fields = ('changed_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('application', 'changed_by')
