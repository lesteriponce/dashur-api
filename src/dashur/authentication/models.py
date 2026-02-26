"""
Custom User model for the Dashur API.
"""
from typing import Optional
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
import logging

logger = logging.getLogger('dashur')


class CustomUserManager(UserManager):
    """Custom user manager that uses email as the unique identifier."""
    
    def create_user(
        self, 
        email: str, 
        password: Optional[str] = None, 
        **extra_fields
    ) -> 'User':
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(
        self, 
        email: str, 
        password: Optional[str] = None, 
        **extra_fields
    ) -> 'User':
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Uses email as the unique identifier instead of username.
    """
    username = None  # Remove username field
    email = models.EmailField(unique=True, verbose_name='Email address')
    first_name = models.CharField(max_length=30, verbose_name='First name')
    last_name = models.CharField(max_length=30, verbose_name='Last name')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone number')
    is_verified = models.BooleanField(default=False, verbose_name='Email verified')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Date of birth')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.email} ({self.get_full_name()})"
    
    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self) -> str:
        """Return the user's short name (first name)."""
        return self.first_name
    
    def get_full_name(self) -> str:
        """Return the user's full name."""
        return self.full_name


class UserProfile(models.Model):
    """
    Extended user profile for additional user information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, verbose_name='Bio')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    website = models.URLField(blank=True, null=True, verbose_name='Website')
    linkedin = models.URLField(blank=True, null=True, verbose_name='LinkedIn profile')
    github = models.URLField(blank=True, null=True, verbose_name='GitHub profile')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='Location')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True, verbose_name='Resume')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} Profile"


class AdminUser(models.Model):
    """
    Admin user model for administrative users.
    Extends the base User model with admin-specific fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_user')
    is_super_admin = models.BooleanField(default=False, verbose_name='Super Admin')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    
    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.user.email} (Admin: {'Super' if self.is_super_admin else 'Regular'})"
    
    @property
    def email(self) -> str:
        """Get the admin user's email."""
        return self.user.email
    
    @property
    def first_name(self) -> str:
        """Get the admin user's first name."""
        return self.user.first_name
    
    @property
    def last_name(self) -> str:
        """Get the admin user's last name."""
        return self.user.last_name
    
    @property
    def full_name(self) -> str:
        """Get the admin user's full name."""
        return self.user.full_name
    
    @property
    def is_active(self) -> bool:
        """Get the admin user's active status."""
        return self.user.is_active
    
    def set_password(self, password: str) -> None:
        """Set the admin user's password."""
        self.user.set_password(password)
        self.user.save()
    
    def save(self, *args, **kwargs) -> None:
        """Override save to ensure the user is also saved."""
        if self.user:
            self.user.save()
        super().save(*args, **kwargs)


# Signal to create UserProfile when User is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created."""
    if created:
        try:
            UserProfile.objects.get_or_create(user=instance)
            logger.info(f"Created profile for user: {instance.email}")
        except Exception as e:
            logger.error(f"Error creating profile for user {instance.email}: {str(e)}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when User is saved."""
    if hasattr(instance, 'profile'):
        try:
            instance.profile.save()
        except Exception as e:
            logger.error(f"Error saving profile for user {instance.email}: {str(e)}")
