"""
Custom validators for the Dashur API.
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    """
    Validate phone number format.
    """
    if not value:
        return
    
    # Remove all non-digit characters
    phone_digits = re.sub(r'[^\d+]', '', value)
    
    # Check if it starts with + (international format) or has valid length
    if not (phone_digits.startswith('+') or len(phone_digits) >= 10):
        raise ValidationError(
            _('Please enter a valid phone number with country code or at least 10 digits.')
        )
    
    # Check total length
    if len(phone_digits) > 15:
        raise ValidationError(
            _('Phone number cannot exceed 15 digits including country code.')
        )


def validate_resume_file(file):
    """
    Validate resume file upload.
    """
    from dashur.utils import validate_file_upload
    
    allowed_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'application/rtf'
    ]
    
    is_valid, error_message = validate_file_upload(
        file,
        allowed_types=allowed_types,
        max_size_mb=5
    )
    
    if not is_valid:
        raise ValidationError(error_message)


def validate_image_file(file):
    """
    Validate image file upload.
    """
    from dashur.utils import validate_file_upload
    
    allowed_types = [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
        'image/webp'
    ]
    
    is_valid, error_message = validate_file_upload(
        file,
        allowed_types=allowed_types,
        max_size_mb=2
    )
    
    if not is_valid:
        raise ValidationError(error_message)


def validate_url(value):
    """
    Validate URL format.
    """
    if not value:
        return
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(value):
        raise ValidationError(_('Please enter a valid URL.'))


# Custom regex validators
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
)

linkedin_validator = RegexValidator(
    regex=r'^https?://(www\.)?linkedin\.com/.+$',
    message=_("Please enter a valid LinkedIn profile URL.")
)

github_validator = RegexValidator(
    regex=r'^https?://(www\.)?github\.com/.+$',
    message=_("Please enter a valid GitHub profile URL.")
)
