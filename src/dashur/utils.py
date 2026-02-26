"""
Utility functions for Dashur API.
"""
import logging
from typing import Optional, Dict, Any, Tuple, Union
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.http import HttpRequest
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger('dashur')


def api_response(
    success: bool = True, 
    data: Optional[Dict[str, Any]] = None, 
    message: str = "Operation successful", 
    status_code: int = status.HTTP_200_OK, 
    errors: Optional[Dict[str, Any]] = None
) -> Response:
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


def validate_file_upload(
    file_obj: Any, 
    allowed_types: Optional[list] = None, 
    max_size_mb: int = 10
) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.
    
    Args:
        file_obj: Uploaded file object
        allowed_types (list): List of allowed MIME types
        max_size_mb (int): Maximum file size in MB
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file_obj:
        return False, "No file provided"
    
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
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_size_bytes:
        return False, f"File size exceeds maximum limit of {max_size_mb}MB"
    
    # Check file type
    if file_obj.content_type not in allowed_types:
        return False, f"File type {file_obj.content_type} is not allowed"
    
    # Check file extension
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.gif']
    file_extension = file_obj.name.lower().split('.')[-1]
    if f'.{file_extension}' not in allowed_extensions:
        return False, f"File extension .{file_extension} is not allowed"
    
    return True, None


def get_client_ip(request: HttpRequest) -> str:
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


def create_admin_user(
    email: str, 
    password: str, 
    first_name: str, 
    last_name: str, 
    is_super_admin: bool = False
) -> Any:
    """
    Create an admin user with hashed password.
    
    Args:
        email (str): Admin email
        password (str): Plain text password
        first_name (str): First name
        last_name (str): Last name
        is_super_admin (bool): Whether user is super admin
    
    Returns:
        AdminUser: Created admin user instance
    """
    from authentication.models import AdminUser, User
    
    # Create the base user first
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_staff=True,
        is_superuser=is_super_admin
    )
    
    # Create the admin user associated with the base user
    admin_user = AdminUser.objects.create(
        user=user,
        is_super_admin=is_super_admin
    )
    
    logger.info(f"Admin user created: {email}")
    return admin_user


def api_response_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
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
            'data': {},
            'message': 'An error occurred',
            'errors': {},
            'timestamp': timezone.now().isoformat(),
        }
        
        # Handle different types of exceptions
        if isinstance(exc, ValidationError):
            custom_response_data['message'] = 'Validation error'
            custom_response_data['errors'] = exc.detail
            response.status_code = status.HTTP_400_BAD_REQUEST
            
        elif isinstance(exc, NotAuthenticated):
            custom_response_data['message'] = 'Authentication required'
            custom_response_data['errors'] = {'detail': 'Authentication credentials were not provided.'}
            response.status_code = status.HTTP_401_UNAUTHORIZED
            
        elif isinstance(exc, PermissionDenied):
            custom_response_data['message'] = 'Permission denied'
            custom_response_data['errors'] = {'detail': 'You do not have permission to perform this action.'}
            response.status_code = status.HTTP_403_FORBIDDEN
            
        elif isinstance(exc, Http404):
            custom_response_data['message'] = 'Resource not found'
            custom_response_data['errors'] = {'detail': 'The requested resource was not found.'}
            response.status_code = status.HTTP_404_NOT_FOUND
            
        else:
            custom_response_data['message'] = str(exc)
            custom_response_data['errors'] = {'detail': str(exc)}
        
        # Log the error
        logger.error(f"API Error: {exc}", exc_info=True)
        
        response.data = custom_response_data
    
    return response


def log_user_activity(
    user: Optional[User], 
    action: str, 
    details: Optional[Dict[str, Any]] = None, 
    request: Optional[HttpRequest] = None
) -> None:
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


