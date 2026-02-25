"""
Models for the contacts app.
"""
from django.db import models
from django.core.validators import RegexValidator
import logging

logger = logging.getLogger('dashur')


class ContactSubmission(models.Model):
    """
    Model for contact form submissions.
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('responded', 'Responded'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    first_name = models.CharField(max_length=50, verbose_name='First Name')
    last_name = models.CharField(max_length=50, verbose_name='Last Name')
    email = models.EmailField(verbose_name='Email Address')
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        verbose_name='Phone Number'
    )
    company = models.CharField(max_length=100, blank=True, null=True, verbose_name='Company')
    subject = models.CharField(max_length=200, verbose_name='Subject')
    message = models.TextField(verbose_name='Message')
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Priority'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Status'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Address')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    referral_source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='How did you hear about us?'
    )
    newsletter_subscription = models.BooleanField(
        default=False,
        verbose_name='Subscribe to newsletter'
    )
    notes = models.TextField(blank=True, null=True, verbose_name='Internal Notes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        db_table = 'contact_submissions'
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"
    
    @property
    def full_name(self):
        """Return the submitter's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_new(self):
        """Check if the submission is new."""
        return self.status == 'new'
    
    @property
    def is_urgent(self):
        """Check if the submission has urgent priority."""
        return self.priority == 'urgent'


class ContactResponse(models.Model):
    """
    Model for responses to contact submissions.
    """
    submission = models.OneToOneField(
        ContactSubmission,
        on_delete=models.CASCADE,
        related_name='response',
        verbose_name='Contact Submission'
    )
    responded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='contact_responses',
        verbose_name='Responded By'
    )
    response_message = models.TextField(verbose_name='Response Message')
    response_email_sent = models.BooleanField(default=False, verbose_name='Email Sent')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Responded At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        db_table = 'contact_responses'
        verbose_name = 'Contact Response'
        verbose_name_plural = 'Contact Responses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Response to {self.submission.full_name}"


# Signal to log contact submission
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ContactSubmission)
def log_contact_submission(sender, instance, created, **kwargs):
    """Log when a new contact submission is created."""
    if created:
        logger.info(f"New contact submission: {instance.full_name} - {instance.subject}")
