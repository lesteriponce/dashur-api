"""
Utility functions for Dashur API.
"""
import logging
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

logger = logging.getLogger('dashur')


def api_response(success=True, data=None, message="Operation successful", status_code=status.HTTP_200_OK, errors=None):
    """
    Create a standardized API response.
    
    Args:
        success (bool): Whether the operation was successful
        data (dict): The response data
        message (str): Response message
        status_code (int): HTTP status code
        errors (dict): Error details if any
    
    Returns:
        Response: DRF Response object
    """
    response_data = {
        'success': success,
        'message': message,
        'timestamp': timezone.now().isoformat(),
    }
    
    if data is not None:
        response_data['data'] = data
    
    if errors is not None:
        response_data['errors'] = errors
    
    return Response(response_data, status=status_code)


def validate_file_upload(file_obj, allowed_types=None, max_size_mb=5):
    """
    Validate uploaded file.
    
    Args:
        file_obj: Uploaded file object
        allowed_types (list): List of allowed MIME types
        max_size_mb (int): Maximum file size in MB
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if allowed_types is None:
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'image/jpeg',
            'image/png',
            'image/gif'
        ]
    
    # Check file size
    if file_obj.size > max_size_mb * 1024 * 1024:
        return False, f"File size must be less than {max_size_mb}MB"
    
    # Check file type
    if file_obj.content_type not in allowed_types:
        return False, f"File type {file_obj.content_type} is not allowed"
    
    return True, None


def get_client_ip(request):
    """
    Get client IP address from request.
    
    Args:
        request: Django request object
    
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def create_admin_user(email, password, first_name, last_name):
    """
    Create an admin user with hashed password.
    
    Args:
        email (str): Admin email
        password (str): Plain text password
        first_name (str): First name
        last_name (str): Last name
    
    Returns:
        User: Created admin user instance
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    admin_user = User.objects.create_superuser(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    logger.info(f"Admin user created: {email}")
    return admin_user


def api_response_exception_handler(exc, context):
    """
    Custom exception handler for consistent API error responses.
    """
    from rest_framework.views import exception_handler
    from django.http import Http404
    from rest_framework.exceptions import ValidationError, PermissionDenied, NotAuthenticated
    
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'message': 'An error occurred',
            'errors': response.data if hasattr(response, 'data') else {'detail': str(exc)},
            'timestamp': timezone.now().isoformat(),
        }
        
        # Handle different types of exceptions
        if isinstance(exc, ValidationError):
            custom_response_data['message'] = 'Validation error'
            
        elif isinstance(exc, NotAuthenticated):
            custom_response_data['message'] = 'Authentication required'
            
        elif isinstance(exc, PermissionDenied):
            custom_response_data['message'] = 'Permission denied'
            
        elif isinstance(exc, Http404):
            custom_response_data['message'] = 'Resource not found'
            
        else:
            custom_response_data['message'] = str(exc)
        
        # Log the error
        logger.error(f"API Error: {exc}", exc_info=True)
        
        response.data = custom_response_data
    
    return response


def log_user_activity(user, action, details=None, request=None):
    """
    Log user activity for audit trail.
    
    Args:
        user: User instance
        action (str): Action performed
        details (dict): Additional details
        request: Django request object (optional)
    """
    activity_data = {
        'user': user.email if user else 'Anonymous',
        'action': action,
        'ip_address': get_client_ip(request) if request else 'Unknown',
        'timestamp': timezone.now().isoformat(),
    }
    
    if details:
        activity_data['details'] = details
    
    logger.info(f"User Activity: {activity_data}")


