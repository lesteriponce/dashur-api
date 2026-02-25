"""
Models for the careers app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import logging

logger = logging.getLogger('dashur')
User = get_user_model()


class JobPosition(models.Model):
    """
    Model for job positions/career opportunities.
    """
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
        ('closed', 'Closed'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Job Title')
    department = models.CharField(max_length=100, verbose_name='Department')
    employment_type = models.CharField(
        max_length=20, 
        choices=EMPLOYMENT_TYPES, 
        default='full_time',
        verbose_name='Employment Type'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name='Status'
    )
    description = models.TextField(verbose_name='Job Description')
    requirements = models.TextField(blank=True, null=True, verbose_name='Requirements')
    responsibilities = models.TextField(blank=True, null=True, verbose_name='Responsibilities')
    benefits = models.TextField(blank=True, null=True, verbose_name='Benefits')
    salary_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name='Minimum Salary'
    )
    salary_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name='Maximum Salary'
    )
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='Location')
    remote_work = models.BooleanField(default=False, verbose_name='Remote Work Available')
    experience_years = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        verbose_name='Years of Experience Required'
    )
    education_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Education Level Required'
    )
    application_deadline = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Application Deadline'
    )
    is_featured = models.BooleanField(default=False, verbose_name='Featured Position')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        db_table = 'job_positions'
        verbose_name = 'Job Position'
        verbose_name_plural = 'Job Positions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'employment_type']),
            models.Index(fields=['department']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.department}"
    
    @property
    def is_active(self):
        """Check if the position is currently active."""
        return self.status == 'active'
    
    @property
    def application_count(self):
        """Get the number of applications for this position."""
        return self.applications.count()
    
    def get_salary_range(self):
        """Return formatted salary range."""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f}"
        elif self.salary_min:
            return f"From ${self.salary_min:,.0f}"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,.0f}"
        return "Competitive"


class JobApplication(models.Model):
    """
    Model for job applications submitted by users.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interviewed', 'Interviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='applications',
        verbose_name='Applicant'
    )
    position = models.ForeignKey(
        JobPosition, 
        on_delete=models.CASCADE, 
        related_name='applications',
        verbose_name='Position'
    )
    first_name = models.CharField(max_length=50, verbose_name='First Name')
    last_name = models.CharField(max_length=50, verbose_name='Last Name')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone')
    resume = models.FileField(
        upload_to='resumes/%Y/%m/', 
        verbose_name='Resume File'
    )
    cover_letter = models.TextField(blank=True, null=True, verbose_name='Cover Letter')
    linkedin_profile = models.URLField(blank=True, null=True, verbose_name='LinkedIn Profile')
    portfolio = models.URLField(blank=True, null=True, verbose_name='Portfolio Website')
    expected_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name='Expected Salary'
    )
    available_start_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Available Start Date'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Application Status'
    )
    notes = models.TextField(blank=True, null=True, verbose_name='Internal Notes')
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='Applied At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        db_table = 'job_applications'
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
        ordering = ['-applied_at']
        unique_together = ['user', 'position']  # One application per user per position
        indexes = [
            models.Index(fields=['status', 'applied_at']),
            models.Index(fields=['position', 'status']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position.title}"
    
    @property
    def full_name(self):
        """Return the applicant's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_pending(self):
        """Check if the application is pending review."""
        return self.status == 'pending'
    
    def can_apply_again(self):
        """Check if user can apply again (for rejected applications)."""
        return self.status in ['rejected', 'withdrawn']


class ApplicationStatusHistory(models.Model):
    """
    Model to track status changes in job applications.
    """
    application = models.ForeignKey(
        JobApplication, 
        on_delete=models.CASCADE, 
        related_name='status_history'
    )
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='status_changes'
    )
    notes = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'application_status_history'
        verbose_name = 'Application Status History'
        verbose_name_plural = 'Application Status Histories'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.application} - {self.old_status} → {self.new_status}"


# Signal to log application creation
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=JobApplication)
def log_application_creation(sender, instance, created, **kwargs):
    """Log when a new job application is created."""
    if created:
        logger.info(f"New job application: {instance.full_name} for {instance.position.title}")
        
        # Create initial status history
        ApplicationStatusHistory.objects.create(
            application=instance,
            old_status=None,
            new_status=instance.status,
            notes="Application submitted"
        )
