"""
Utility functions for the Dashur API project.
"""
import logging
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('dashur')


def api_response(success=True, data=None, message="Operation successful", errors=None, status_code=status.HTTP_200_OK):
    """
    Standard API response format for consistent JSON responses.
    
    Args:
        success (bool): Whether the operation was successful
        data (dict): The response data
        message (str): Response message
        errors (dict/list): Error details if any
        status_code (int): HTTP status code
    
    Returns:
        Response: DRF Response object with consistent format
    """
    response_data = {
        'success': success,
        'data': data or {},
        'message': message,
        'errors': errors
    }
    
    return Response(response_data, status=status_code)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses.
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
            'errors': {}
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
        
        response.data = custom_response_data
        
        # Log the error
        logger.error(f"API Error: {exc}", exc_info=True)
    
    return response


def validate_file_upload(file, allowed_types=None, max_size_mb=10):
    """
    Validate uploaded files for security.
    
    Args:
        file: Uploaded file object
        allowed_types (list): List of allowed MIME types
        max_size_mb (int): Maximum file size in MB
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        return False, f"File size exceeds maximum limit of {max_size_mb}MB"
    
    # Check file type
    if allowed_types:
        if file.content_type not in allowed_types:
            return False, f"File type {file.content_type} is not allowed"
    
    # Check file extension
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png']
    file_extension = file.name.lower().split('.')[-1]
    if f'.{file_extension}' not in allowed_extensions:
        return False, f"File extension .{file_extension} is not allowed"
    
    return True, None


def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_admin_user(email, password, first_name, last_name, is_super_admin=False):
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
    from authentication.models import AdminUser
    
    admin_user = AdminUser(
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_super_admin=is_super_admin,
        is_active=True
    )
    admin_user.set_password(password)
    admin_user.save()
    
    logger.info(f"Admin user created: {email}")
    return admin_user
