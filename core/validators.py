"""
Shared file validation utilities.
"""
from django.core.exceptions import ValidationError


# File upload limits
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp', 'image/gif']


def validate_uploaded_file(file, file_description='File'):
    """
    Validate uploaded file size and type.
    
    Args:
        file: Uploaded file object
        file_description: Human-readable name for error messages
    
    Raises:
        ValidationError: If file is invalid
    """
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f'{file_description} size must be less than 5MB. '
            f'Your file is {file.size / (1024 * 1024):.2f}MB.'
        )
    
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(
            f'{file_description} must be a valid image file (JPEG, PNG, WEBP, or GIF). '
            f'Received: {file.content_type}'
        )
