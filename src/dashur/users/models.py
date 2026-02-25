"""
Models for the users app.
This app extends the authentication app with additional user-related functionality.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserActivity(models.Model):
    """
    Model to track user activity and audit logs.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name='User'
    )
    action = models.CharField(max_length=100, verbose_name='Action')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Address')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp}"


class UserSession(models.Model):
    """
    Model to track user sessions for security monitoring.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='User'
    )
    session_key = models.CharField(max_length=40, unique=True, verbose_name='Session Key')
    ip_address = models.GenericIPAddressField(verbose_name='IP Address')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Last Activity')
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.session_key[:8]}..."


class UserPreference(models.Model):
    """
    Model to store user preferences and settings.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences',
        verbose_name='User'
    )
    language = models.CharField(max_length=10, default='en', verbose_name='Language')
    timezone = models.CharField(max_length=50, default='UTC', verbose_name='Timezone')
    email_notifications = models.BooleanField(default=True, verbose_name='Email Notifications')
    push_notifications = models.BooleanField(default=True, verbose_name='Push Notifications')
    marketing_emails = models.BooleanField(default=False, verbose_name='Marketing Emails')
    theme = models.CharField(max_length=20, default='light', verbose_name='Theme')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        db_table = 'user_preferences'
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"{self.user.email} Preferences"


# Signal to create UserPreference when User is created
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger('dashur')

@receiver(post_save, sender=User)
def create_user_preference(sender, instance, created, **kwargs):
    """Create a UserPreference when a new User is created."""
    if created:
        try:
            UserPreference.objects.get_or_create(user=instance)
            logger.info(f"Created preferences for user: {instance.email}")
        except Exception as e:
            logger.error(f"Error creating preferences for user {instance.email}: {str(e)}")

@receiver(post_save, sender=User)
def save_user_preference(sender, instance, **kwargs):
    """Save the UserPreference when User is saved."""
    if hasattr(instance, 'preferences'):
        try:
            instance.preferences.save()
        except Exception as e:
            logger.error(f"Error saving preferences for user {instance.email}: {str(e)}")
